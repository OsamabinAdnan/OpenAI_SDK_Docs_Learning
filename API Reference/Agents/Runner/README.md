# Workflow of Runner (Class) Comparison

| Feature / Aspect | **run: Async Run** | **run_sync: Synchronous Run** | **run_streamed: Streaming Run** |
|------------------|--------------------|-------------------------------|---------------------------------|
| **Mode** | Standard workflow run (default async-friendly). | Synchronous wrapper around `run()`. | Streaming mode (returns events as they happen). |
| **Event Loop** | Works normally with async contexts. | ❌ Does **not** work inside existing event loops (e.g. Jupyter, FastAPI, async functions). | ✅ Works with async, designed for live streaming. |
| **Result** | Final run result with inputs, guardrail results, and last agent output. | Final run result with inputs, guardrail results, and last agent output. | Result object + a method to stream semantic events as they’re generated. |
| **Loop Logic** | 1. Agent runs with input.<br>2. If final output → stop.<br>3. If handoff → new agent.<br>4. Else → run tools and repeat. | 1. Agent runs with input.<br>2. If final output → stop.<br>3. If handoff → new agent.<br>4. Else → run tools and repeat. | 1. Agent runs with input.<br>2. If final output → stop.<br>3. If handoff → new agent.<br>4. Else → run tools and repeat. |
| **Exceptions** | - `MaxTurnsExceeded` if too many turns.<br>- `GuardrailTripwireTriggered` if a guardrail is hit.<br>(Only first agent’s input guardrails run). | - `MaxTurnsExceeded` if too many turns.<br>- `GuardrailTripwireTriggered` if a guardrail is hit.<br>(Only first agent’s input guardrails run). | - `MaxTurnsExceeded` if too many turns.<br>- `GuardrailTripwireTriggered` if a guardrail is hit.<br>(Only first agent’s input guardrails run). |
| **Arguments** | `starting_agent`, `input`, `context`, `max_turns`, `hooks`, `run_config`, `previous_response_id`, `conversation_id`, `session`. | `starting_agent`, `input`, `context`, `max_turns`, `hooks`, `run_config`, `previous_response_id`, `conversation_id`, `session`, but **conversation_id** described as “stored conversation ID.” | `starting_agent`, `input`, `context`, `max_turns`, `hooks`, `run_config`, `previous_response_id`, `conversation_id`, `session`, but return value differs. |
| **Returns** | Run result (inputs, guardrail results, final output). | Run result (inputs, guardrail results, final output). | Result object **with streaming support**. |

---

👉 **In short**:  
- **run = Normal run** (default async-friendly).  
- **run_sync = Blocking sync run** (use when you can’t use async, but not in Jupyter/async apps).  
- **run_streamed = Streaming run** (lets you stream events live).  


Click [API Reference/Agents/Runner](https://openai.github.io/openai-agents-python/ref/run/) for more details.

---