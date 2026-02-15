"""
Requirements: pip install langchain langchain-core openai opentelemetry-api opentelemetry-sdk
"""

from typing import Callable, Any
import time
import logging
import re

# LangChain middleware & agent imports 
from langchain.agents.middleware import (
    AgentMiddleware,
    hook_config,
    before_model,
    after_model,
    wrap_model_call,
    ModelRequest,
    ModelResponse,
    AgentState,
)
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import Tool
from langchain.messages import AIMessage

# Optional: OpenTelemetry (demo integration)
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

# Basic logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent_hooks_example")

# Init simple OpenTelemetry console exporter for demo (production: use jaeger/OTLP exporter)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
tracer = trace.get_tracer(__name__)


class TelemetryLoggingMiddleware(AgentMiddleware):
    """
    Node-style middleware that logs and emits OpenTelemetry spans for model calls.
    Keep simple: fail safe (errors in this middleware should not crash agent).
    """
    def before_model(self, state: AgentState, runtime: Any) -> dict[str, Any] | None:
        try:
            # lightweight context we care about
            last_user = ""
            if state.get("messages"):
                last_user = state["messages"][-1].content
            logger.info("before_model: user_prompt_len=%d", len(last_user))
            # create a span for this model call
            span = tracer.start_span("agent.model.call")
            # store span in state for after_model to end it
            return {"_telemetry_span_id": id(span)}
        except Exception as e:
            logger.exception("Telemetry before_model failed: %s", e)
            return None

    def after_model(self, state: AgentState, runtime: Any) -> dict[str, Any] | None:
        try:
            # end the span if present (demo only; LangChain runtime may manage lifecycle differently)
            # In production, we'd use context manager or proper instrumentation
            logger.info("after_model: last_message_preview=%s", state["messages"][-1].content[:120])
            return None
        except Exception as e:
            logger.exception("Telemetry after_model failed: %s", e)
            return None


class PIIBlockMiddleware(AgentMiddleware):
    """
    Node-style middleware which inspects the last user message and blocks execution
    returning a friendly message and jumping to the end. Uses decorator-based hook_config
    to declare allowed jump targets.
    """
    @hook_config(can_jump_to=["end"])
    def before_model(self, state: AgentState, runtime: Any) -> dict[str, Any] | None:
        try:
            # extremely simple PII detector (placeholder). Replace with a real model or regex set.
            last = state.get("messages", [])[-1].content if state.get("messages") else ""
            # Basic patterns: email, ssn-like, phone
            if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", last) or re.search(r"\b\d{3}[- ]?\d{2}[- ]?\d{4}\b", last):
                # Block and jump to end with a safe message
                return {
                    "messages": [AIMessage("I cannot process requests containing personal or sensitive identifiers.")],
                    "jump_to": "end"
                }
            return None
        except Exception as e:
            logger.exception("PIIBlockMiddleware error: %s", e)
            # Do not block the agent on middleware failure
            return None


class RetryModelMiddleware(AgentMiddleware):
    """
    Wrap-style middleware that retries model calls up to max_retries upon transient exceptions.
    Demonstrates wrap_model_call semantics: you receive (request, handler) and must return ModelResponse.
    """
    def __init__(self, max_retries: int = 3, backoff_seconds: float = 0.5):
        super().__init__()
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

    def wrap_model_call(self, request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
        last_exc = None
        for attempt in range(1, self.max_retries + 1):
            try:
                start = time.time()
                resp = handler(request)  # call the next middleware or actual model
                duration = time.time() - start
                logger.info("Model call succeeded in %.3fs (attempt %d)", duration, attempt)
                return resp
            except Exception as e:
                last_exc = e
                logger.warning("Model call attempt %d failed: %s", attempt, e)
                if attempt < self.max_retries:
                    time.sleep(self.backoff_seconds * attempt)
                else:
                    logger.error("All retries exhausted for model call.")
                    raise last_exc


def make_simple_tool():
    """
    A trivial tool for demo purposes: returns a simple string.
    """
    def _time_tool(query: str) -> str:
        return f"Tool answered: received '{query}'"
    return Tool.from_function(_time_tool, name="echo_tool", description="Echo tool for demo")


def main():
    # Initialize a lightweight chat model (swap provider to your credentials/choice)
    # Replace model name with your available model. This uses LangChain's model init helper.
    model = init_chat_model("gpt-4o-mini")  # replace per your provider / API key config

    # Attach middleware in desired order. Execution order matters for before/after/wrap hooks.
    middleware = [
        TelemetryLoggingMiddleware(),
        PIIBlockMiddleware(),
        RetryModelMiddleware(max_retries=2, backoff_seconds=0.2),
    ]

    # Create agent with a demo tool and middleware
    agent = create_agent(
        model=model,
        tools=[make_simple_tool()],
        middleware=middleware,
    )

    # Demonstration: safe prompt
    print("Running safe prompt...")
    res_safe = agent.run("Hello agent, echo 'test' please.")
    print("Agent output (safe):", res_safe)

    # Demonstration: blocked prompt (contains an email)
    print("\nRunning blocked prompt (contains email)...")
    try:
        res_blocked = agent.run("Please send this to alice@example.com and also tell me the plan.")
        print("Agent output (blocked):", res_blocked)
    except Exception as e:
        # agent.run could raise depending on runtime; handle gracefully
        logger.exception("Agent invocation error: %s", e)


if __name__ == "__main__":
    main()
