# **Tracing**

It is abuilt-in feature in openai agent sdk, who record important events, when agent run,it shown workflow, like LLM Generations, Function Tool call, handsoff , guardrails, custom events.

- By default , `tracing is on`. You can see the whole workflow on openai dashboard.
- if you want to disable tracing, write
- config=RunConfig(tracing_disabled=True) 

## **Traces Vs Span:**

- `Traces:` a one trace is a full workflow record like:
- `Workflow_name:` by deafult it name is Agent_Workflow
- `trace_id:` auto generated unique id
- `group_id:` multiple traces from the same conversation
- `metadata:` custom info for debugging (optional)

`Spans:` is a parts of traces means a small record of a operation
- Inside traces, a multiple spans are there.
- Every span captured a specific action like:

    * `agent-span (start-at, end-at timestamps):` when agent run
    * `generation-span:` when llm generate repsonse
    * `function-span:` when tool calling
    * `guardrail-span:` when guardrail run
    * `handoff-span:` when a agent give control to another agent
    * `transcription-span:` use to audio inputs(speech to text)
    * `speech-span:` use for audio outputs(text to speech)


- Every span has a parent id, so it make in hierarchy.
- Runner.run always make trace

## **Multi run traces(Highr level traces): when two run in one agent**

- Note: You can control your traces because sometimes sensitive data can captured
- RunConfig.trace_include_sensitive_data = False