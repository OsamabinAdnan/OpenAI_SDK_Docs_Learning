# **Running Agents**

You can run agents via the `Runner` class. You have three options:
1. `Runner.run()` – asynchronous, returns a `RunResult`.
2. `Runner.run_sync()` – synchronous, calls `.run()` internally.
3. `Runner.run_streamed()` – asynchronous, returns a `RunResultStreaming`.
    * Runs the LLM in streaming mode.
    * Streams events as they are received.

### **Example**
```python
from agents import Agent, Runner

async def main():
    agent = Agent(name="Assistant", instructions="You are a helpful assistant")

    result = await Runner.run(agent, "Write a haiku about recursion in programming.")
    print(result.final_output)
    # Code within the code,
    # Functions calling themselves,
    # Infinite loop's dance
```

## **The Agent Loop**

When you use `Runner.run()`, you pass in a starting agent and input.

* Input can be a string (user message) or a list of input items (OpenAI Responses API format).

The loop works as follows:
1. Runner calls the LLM for the current agent with the given input.
2. The LLM produces its output:

    * If `final_output` → loop ends and result is returned.
    * If handoff → runner switches to the new agent and continues the loop.
    * If tool calls → runner executes the tools, appends results, and re-runs the loop.

3. If `max_turns` is exceeded → raises `MaxTurnsExceeded`.
A run is considered final output only if:

    * The output matches the agent’s `output_type`.
    * No tool calls are present.

## **Streaming**

* Use `Runner.run_streamed()` for streaming responses.
* Returns `RunResultStreaming`, which contains the complete run details once finished.
* You can call `.stream_events()` to iterate over streaming events in real time.

## **Run Config**

The `run_config` parameter lets you configure global run settings:

* `model` – Override agent’s model.
* `model_provider` – Define provider (default = OpenAI).
* `model_settings` – Override parameters (e.g., `temperature`, `top_p`).
* `input_guardrails`, `output_guardrails` – Add guardrails for safety.
* `handoff_input_filter` – Apply global filter to inputs before handoff.
* `tracing_disabled` – Disable tracing entirely.
* `trace_include_sensitive_data` – Configure sensitive data inclusion.
* `workflow_name`, `trace_id`, `group_id` – Tracing metadata fields.
* `trace_metadata` – Add custom metadata to traces.

## **Conversations / Chat Threads**

One `Runner.run()` call may involve multiple agents/tools, but it represents a single logical chat turn.

### Example Flow

- **User turn**: User enters a question.
- **Runner run**: Agent calls LLM, runs tools, performs handoff, produces output.
- **At the end**, you can:
  - Show all generated items.
  - Or just the final output.
- For follow-ups, call `Runner.run()` again.

## **Manual Conversation Management**

Use `RunResultBase.to_input_list()` to manage history manually.

```python
async def main():
    agent = Agent(name="Assistant", instructions="Reply very concisely.")
    thread_id = "thread_123"

    # First turn
    result = await Runner.run(agent, "What city is the Golden Gate Bridge in?")
    print(result.final_output)  # San Francisco

    # Second turn
    new_input = result.to_input_list() + [{"role": "user", "content": "What state is it in?"}]
    result = await Runner.run(agent, new_input)
    print(result.final_output)  # California
```

## **Automatic Conversation Management (Sessions)**

Use SQLiteSession (or other session backends) to store conversation history automatically:

```python
from agents import Agent, Runner, SQLiteSession

async def main():
    agent = Agent(name="Assistant", instructions="Reply very concisely.")
    session = SQLiteSession("conversation_123")

    # First turn
    result = await Runner.run(agent, "What city is the Golden Gate Bridge in?", session=session)
    print(result.final_output)  # San Francisco

    # Second turn (remembers context automatically)
    result = await Runner.run(agent, "What state is it in?", session=session)
    print(result.final_output)  # California
```

**Sessions handle:**
* Retrieving past conversation history.
* Storing new messages.
* Keeping separate histories per session ID.

### **Long-Running Agents & Human-in-the-Loop**

* The Agents SDK integrates with Temporal for durable, long-running workflows.
* Supports human-in-the-loop tasks.
* Useful for tasks requiring pauses, retries, or external approvals.

### **Exceptions**
The SDK raises exceptions during runs:

* `AgentsException` – Base class for all exceptions.
* `MaxTurnsExceeded` – Raised when `max_turns` is reached.
* `ModelBehaviorError` – LLM produced invalid or malformed outputs.
* `UserError` – Developer misconfiguration or misuse of API.
* `InputGuardrailTripwireTriggered` – Input guardrail condition met.
* `OutputGuardrailTripwireTriggered` – Output guardrail condition met.