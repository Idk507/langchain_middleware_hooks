# LangChain Agent Hooks - Complete Usage Guide

This guide provides detailed information on using the LangChain agent hooks implementation.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Middleware Types](#middleware-types)
3. [Hook Types](#hook-types)
4. [Custom State](#custom-state)
5. [Execution Order](#execution-order)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

## Step 1: Get Azure OpenAI Access

### Prerequisites
- Active Azure subscription
- Azure OpenAI access approved (may require application)

### Request Access
1. Go to https://aka.ms/oai/access
2. Fill out the application form
3. Wait for approval (can take a few days)

## Step 2: Create Azure OpenAI Resource

### In Azure Portal

1. **Navigate to Azure Portal**
   - Go to https://portal.azure.com/
   - Sign in with your Azure account

2. **Create Resource**
   - Click "Create a resource"
   - Search for "Azure OpenAI"
   - Click "Create"

3. **Configure Resource**
   - **Subscription**: Select your subscription
   - **Resource group**: Create new or select existing
   - **Region**: Choose a region (e.g., East US, West Europe)
   - **Name**: Choose a unique name (e.g., `my-openai-resource`)
   - **Pricing tier**: Select Standard S0

4. **Review and Create**
   - Click "Review + create"
   - Click "Create"
   - Wait for deployment to complete

## Step 3: Deploy Models

### Deploy GPT-4o-mini (Simple Model)

1. **Navigate to Your Resource**
   - Go to your Azure OpenAI resource
   - Click on "Model deployments" in the left menu
   - Click "Create new deployment"

2. **Configure Deployment**
   - **Select a model**: Choose `gpt-4o-mini`
   - **Deployment name**: `gpt-4o-mini` (or your preferred name)
   - **Model version**: Select latest version
   - **Deployment type**: Standard
   - Click "Create"

### Deploy GPT-4o (Complex Model)

1. **Create Another Deployment**
   - Click "Create new deployment" again

2. **Configure Deployment**
   - **Select a model**: Choose `gpt-4o`
   - **Deployment name**: `gpt-4o` (or your preferred name)
   - **Model version**: Select latest version
   - **Deployment type**: Standard
   - Click "Create"

## Step 4: Get Credentials

### Get API Key and Endpoint

1. **Navigate to Keys and Endpoint**
   - In your Azure OpenAI resource
   - Click "Keys and Endpoint" in the left menu

2. **Copy Information**
   - **KEY 1**: This is your `AZURE_OPENAI_API_KEY`
   - **Endpoint**: This is your `AZURE_OPENAI_ENDPOINT`
   - Keep these secure!

## Step 5: Configure Project

### Update .env File

Create/edit `.env` file with your credentials:

```bash
# Azure OpenAI API Key (from Keys and Endpoint)
AZURE_OPENAI_API_KEY=abc123def456...

# Azure OpenAI Endpoint (from Keys and Endpoint)
AZURE_OPENAI_ENDPOINT=https://my-openai-resource.openai.azure.com/

# API Version (recommended, check Azure docs for latest)
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Deployment Names (must match what you created)
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_GPT4_DEPLOYMENT_NAME=gpt-4o
```


## Step 6: Test Connection

### Run Basic Example

```bash
python examples/basic_azure_example.py
```

If successful, you should see:
- ✓ Azure configuration printed
- ✓ Agent making calls
- ✓ Responses from your Azure OpenAI deployments

## Common Issues and Solutions

### Issue: "Access Denied" or "Unauthorized"

**Cause**: Invalid API key or endpoint

**Solution**:
1. Double-check your API key in Azure Portal
2. Ensure endpoint URL is correct (includes https:// and trailing /)
3. Verify the key hasn't been regenerated

### Issue: "Deployment not found"

**Cause**: Deployment name mismatch

**Solution**:
1. Go to Azure Portal → Your Resource → Model deployments
2. Check exact deployment names
3. Update `.env` to match exactly (case-sensitive)

### Issue: "Region not available"

**Cause**: Azure OpenAI not available in selected region

**Solution**:
1. Check available regions: https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models
2. Create resource in an available region (e.g., East US, West Europe)

### Issue: "Quota exceeded"

**Cause**: Rate limits or quota limits reached

**Solution**:
1. Check quota in Azure Portal → Your Resource → Quotas
2. Request quota increase if needed
3. Implement rate limiting in your code

### Issue: "Model not available"

**Cause**: Model not available in your region or subscription

**Solution**:
1. Check model availability for your region
2. Try a different model (e.g., gpt-35-turbo instead of gpt-4)
3. Contact Azure support for access

## Best Practices

### Security

1. **Never commit `.env` file**
   - Add to `.gitignore`
   - Keep credentials secure

2. **Use Azure Key Vault**
   - For production deployments
   - Rotate keys regularly

3. **Implement Rate Limiting**
   - Prevent quota exhaustion
   - Control costs

### Cost Management

1. **Monitor Usage**
   - Check Azure Portal → Cost Management
   - Set up billing alerts

2. **Choose Right Models**
   - Use GPT-4o-mini for simple tasks
   - Reserve GPT-4 for complex queries

3. **Implement Caching**
   - Cache frequent responses
   - Reduce API calls

### Performance

1. **Select Appropriate Region**
   - Choose region close to users
   - Consider latency requirements

2. **Use Latest API Version**
   - Better features and performance
   - Check documentation regularly

3. **Optimize Prompts**
   - Shorter prompts = faster responses
   - Clear instructions = better results

## Deployment Models Comparison

| Model | Best For | Speed | Cost | Capabilities |
|-------|----------|-------|------|--------------|
| GPT-4o-mini | Simple queries, fast responses | Fast | Low | Good for basic tasks |
| GPT-4o | Complex analysis, high quality | Moderate | Higher | Best for advanced tasks |
| GPT-4 | Maximum quality, complex reasoning | Slower | Highest | Best capabilities |

## API Versions

Always use the latest stable API version. Check:
https://learn.microsoft.com/en-us/azure/ai-services/openai/reference

Current recommended: `2024-02-15-preview`


### Installation

```bash
# Run the quick start script
./quickstart.sh

# Or manually:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt --break-system-packages
cp .env.example .env
# Edit .env with your API keys
```

### First Agent

```python
from langchain.agents import create_agent
from middleware.logging_middleware import log_before_model, log_after_model

agent = create_agent(
    model="gpt-4o-mini",
    middleware=[log_before_model, log_after_model],
    tools=[],
)

result = agent.invoke({"messages": [{"role": "user", "content": "Hello!"}]})
```

---

## Middleware Types

### 1. Decorator-Based Middleware

**Best for:** Simple, single-purpose hooks

```python
from langchain.agents.middleware import before_model, after_model

@before_model
def my_hook(state, runtime):
    print("Before model call")
    return None  # or dict with state updates

@after_model
def my_other_hook(state, runtime):
    print("After model call")
    return None
```

**Pros:**
- Simple and concise
- Quick to implement
- Good for one-off functionality

**Cons:**
- Can't combine multiple hooks in one component
- No configuration options
- Can't have both sync and async versions

### 2. Class-Based Middleware

**Best for:** Complex middleware with multiple hooks or configuration

```python
from langchain.agents.middleware import AgentMiddleware

class MyMiddleware(AgentMiddleware):
    def __init__(self, config_value):
        super().__init__()
        self.config = config_value
    
    def before_model(self, state, runtime):
        # Hook implementation
        return None
    
    def after_model(self, state, runtime):
        # Hook implementation
        return None
```

**Pros:**
- Can combine multiple hooks
- Configurable via `__init__`
- Reusable across projects
- Can maintain internal state

**Cons:**
- More verbose
- Requires class structure

---

## Hook Types

### Node-Style Hooks

Run sequentially at specific points. Use for logging, validation, state updates.

#### `before_agent`
- Runs **once** at the start of agent execution
- Good for: Initialization, setup, logging start

```python
@before_agent
def initialize(state, runtime):
    return {"start_time": time.time()}
```

#### `before_model`
- Runs **before each** model call
- Good for: Pre-call validation, logging, state checks

```python
@before_model
@hook_config(can_jump_to=["end"])
def check_limit(state, runtime):
    if len(state["messages"]) > 50:
        return {"jump_to": "end"}
    return None
```

#### `after_model`
- Runs **after each** model response
- Good for: Response logging, state updates, tracking

```python
@after_model
def track_usage(state, runtime):
    # Track tokens, update counters, etc.
    return {"model_calls": state.get("model_calls", 0) + 1}
```

#### `after_agent`
- Runs **once** at the end of agent execution
- Good for: Cleanup, final logging, statistics

```python
@after_agent
def finalize(state, runtime):
    print(f"Total messages: {len(state['messages'])}")
    return None
```

### Wrap-Style Hooks

Wrap execution and control when/if the handler is called.

#### `wrap_model_call`
- Wraps each model invocation
- You control if/when/how many times the handler is called
- Good for: Retry logic, caching, fallbacks

```python
@wrap_model_call
def retry_wrapper(request, handler):
    for attempt in range(3):
        try:
            return handler(request)
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
```

#### `wrap_tool_call`
- Wraps each tool invocation
- Good for: Tool monitoring, error handling, rate limiting

```python
@wrap_tool_call
def monitor_tool(request, handler):
    print(f"Calling tool: {request.tool_call['name']}")
    result = handler(request)
    print(f"Tool completed")
    return result
```

---

## Custom State

### Defining Custom State

```python
from langchain.agents.middleware import AgentState
from typing_extensions import NotRequired

class MyState(AgentState):
    user_id: NotRequired[str]
    call_count: NotRequired[int]
    custom_data: NotRequired[dict]
```

### Using Custom State (Decorator)

```python
@before_model(state_schema=MyState)
def my_hook(state: MyState, runtime):
    user_id = state.get("user_id", "unknown")
    # Use typed state
    return None
```

### Using Custom State (Class)

```python
class MyMiddleware(AgentMiddleware[MyState]):
    state_schema = MyState
    
    def before_model(self, state: MyState, runtime):
        # Fully typed state access
        count = state.get("call_count", 0)
        return {"call_count": count + 1}
```

### Invoking with Custom State

```python
result = agent.invoke({
    "messages": [HumanMessage(content="Hello")],
    "user_id": "user123",
    "call_count": 0,
    "custom_data": {"preferences": "concise"},
})
```

---

## Execution Order

### Multiple Middleware

```python
agent = create_agent(
    model="gpt-4o-mini",
    middleware=[mw1, mw2, mw3],
    tools=[...],
)
```

**Execution Flow:**

1. `mw1.before_agent()`
2. `mw2.before_agent()`
3. `mw3.before_agent()`

**For each model call:**

4. `mw1.before_model()`
5. `mw2.before_model()`
6. `mw3.before_model()`
7. `mw1.wrap_model_call()` wraps `mw2.wrap_model_call()` wraps `mw3.wrap_model_call()` wraps actual call
8. `mw3.after_model()`
9. `mw2.after_model()`
10. `mw1.after_model()`

**At end:**

11. `mw3.after_agent()`
12. `mw2.after_agent()`
13. `mw1.after_agent()`

### Key Rules

- `before_*` hooks: First to last
- `after_*` hooks: Last to first (reverse order)
- `wrap_*` hooks: Nested (first wraps all others)

---

## Best Practices

### 1. Hook Selection

- **Logging/validation**: Use node-style hooks (`before_*`, `after_*`)
- **Retry/caching/fallback**: Use wrap-style hooks (`wrap_*`)
- **State updates**: Use node-style hooks
- **Error handling**: Use wrap-style hooks

### 2. Error Handling

Always handle errors gracefully:

```python
@before_model
def safe_hook(state, runtime):
    try:
        # Your logic
        return {"key": "value"}
    except Exception as e:
        logger.error(f"Hook failed: {e}")
        return None  # Don't crash the agent
```

### 3. State Updates

Return dictionaries to update state:

```python
@after_model
def update_state(state, runtime):
    return {
        "model_calls": state.get("model_calls", 0) + 1,
        "last_call_time": time.time(),
    }
```

### 4. Early Exit with Jumps

Use `jump_to` to exit early:

```python
@before_model
@hook_config(can_jump_to=["end"])
def check_limit(state, runtime):
    if should_stop(state):
        return {
            "messages": [AIMessage(content="Limit reached")],
            "jump_to": "end"
        }
    return None
```

Available jump targets:
- `"end"` - Jump to end (or first `after_agent` hook)
- `"tools"` - Jump to tools node
- `"model"` - Jump to model node (or first `before_model` hook)

### 5. Middleware Order

Place middleware in logical order:

```python
# Good order:
middleware=[
    safety_check,      # Check safety first
    rate_limiter,      # Then check quotas
    model_selector,    # Select appropriate model
    retry_handler,     # Handle failures
    logger,            # Log everything
]
```

### 6. Testing

Test middleware independently:

```python
def test_my_middleware():
    mw = MyMiddleware()
    state = {"messages": []}
    runtime = Mock()
    
    result = mw.before_model(state, runtime)
    assert result is not None
```

---

## Troubleshooting

### Issue: "Model call failed"

**Cause:** API key not set or invalid

**Solution:**
```bash
# Check your .env file
cat .env
# Ensure OPENAI_API_KEY is set correctly
```

### Issue: "Rate limit exceeded"

**Cause:** Too many API calls

**Solution:**
- Increase `max_calls_per_minute` in `RateLimitMiddleware`
- Add retry logic
- Implement caching

### Issue: "Middleware not executing"

**Cause:** Incorrect return value or exception

**Solution:**
- Ensure hooks return `None` or `dict`
- Add error handling
- Check logs for exceptions

### Issue: "State not updating"

**Cause:** Not returning state updates

**Solution:**
```python
# Wrong:
def my_hook(state, runtime):
    state["key"] = "value"  # ❌ Direct mutation doesn't work
    return None

# Right:
def my_hook(state, runtime):
    return {"key": "value"}  # ✓ Return updates
```

### Issue: "Jump not working"

**Cause:** Missing `hook_config` decorator

**Solution:**
```python
# Wrong:
@before_model
def my_hook(state, runtime):
    return {"jump_to": "end"}  # ❌ Won't work

# Right:
@before_model
@hook_config(can_jump_to=["end"])  # ✓ Must declare jump targets
def my_hook(state, runtime):
    return {"jump_to": "end"}
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or for specific middleware:
mw = LoggingMiddleware(log_level="DEBUG")
```

---

## Advanced Patterns

### Pattern 1: Conditional Middleware

```python
class ConditionalMiddleware(AgentMiddleware):
    def __init__(self, enabled=True):
        super().__init__()
        self.enabled = enabled
    
    def before_model(self, state, runtime):
        if not self.enabled:
            return None
        # Execute hook logic
        return {"key": "value"}
```

### Pattern 2: Middleware Chain

```python
def create_middleware_chain(*middleware_classes):
    """Create a chain of middleware instances."""
    return [mw() for mw in middleware_classes]

middleware = create_middleware_chain(
    LoggingMiddleware,
    RetryMiddleware,
    RateLimitMiddleware,
)
```

### Pattern 3: Context Injection

```python
class ContextMiddleware(AgentMiddleware):
    def wrap_model_call(self, request, handler):
        # Inject additional context
        system_msg = request.system_message
        new_content = list(system_msg.content_blocks) + [
            {"type": "text", "text": "Additional context here"}
        ]
        new_msg = SystemMessage(content=new_content)
        return handler(request.override(system_message=new_msg))
```

---

## Additional Resources

- [LangChain Documentation](https://docs.langchain.com/)
- [Middleware API Reference](https://reference.langchain.com/python/langchain/middleware/)
- [Example Projects](./examples/)
- [Test Suite](./tests/)

- **Azure OpenAI Documentation**: https://learn.microsoft.com/en-us/azure/ai-services/openai/
- **Model Availability**: https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models
- **Pricing**: https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/
- **Quotas and Limits**: https://learn.microsoft.com/en-us/azure/ai-services/openai/quotas-limits
- **Request Access**: https://aka.ms/oai/access

