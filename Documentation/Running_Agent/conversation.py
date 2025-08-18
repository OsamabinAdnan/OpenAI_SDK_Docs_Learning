from agents import (
    Agent, Runner, function_tool, OpenAIChatCompletionsModel, RunConfig, set_tracing_disabled, RunContextWrapper, ModelSettings, StopAtTools, FunctionToolResult, ToolsToFinalOutputResult, ModelSettings, trace, SQLiteSession
)
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
from rich import print
from dataclasses import dataclass
from pydantic import BaseModel
from typing import Any, List
import asyncio

load_dotenv()

set_tracing_disabled(True)


gemini_api_key=os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise Exception("GEMINI_API_KEY is not set. Please set it in the .env file.")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client,
)

#---------------------------- Run config ----------------------------
run_config = RunConfig(
    model=model,
    tracing_disabled=True,
    model_provider=external_client,
    model_settings=ModelSettings(
        max_tokens=200,
        temperature=0.7,
        top_p=0.3,
        # frequency_penalty=0.2,
        presence_penalty=0.2,
    ),
    # input_guardrails=
    # output_guardrails=
    # handoff_input_filter=None,
    # trace_include_sensitive_data=
    # workflow_name=
    # trace_id=
    # group_id=
    # trace_metadata=None,
)

async def main():
    # ---------------------------- Manual conversation management ----------------------------

    # agent = Agent(name="Assistant", instructions="Reply very concisely.", model=model)

    # thread_id = "thread_123" # Example thread ID
    # with trace(workflow_name="Conversation", group_id=thread_id):
    #     # First Run
    #     result = await Runner.run(agent, "What city is the Golden Gate Bridge in?")
    #     print("First Run: ",result.final_output)
    #     # San Francisco

    #     # Second turn
    #     new_input = result.to_input_list() + [{"role": "user", "content": "What state is it in?"}]
    #     result = await Runner.run(agent, new_input)
    #     print("Second Run: ",result.final_output)
    #     # California

    #  ---------------------------- Automatic conversation management with Sessions ----------------------------

    agent = Agent(name="Assistant", instructions="Reply very concisely.", model=model)

    thread_id = "thread_123"  # Example thread ID
    session = SQLiteSession("conversation_123")

    with trace(workflow_name="Conversation", group_id=thread_id):
        # First turn
        result = await Runner.run(agent, "What city is the Golden Gate Bridge in?", session=session)
        print("First Run: ",result.final_output)
        # San Francisco

        # Second turn - agent automatically remembers previous context
        result = await Runner.run(agent, "What state is it in?", session=session)
        print("Second Run: ",result.final_output)
        # California

asyncio.run(main())