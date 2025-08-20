#---------------------------- Running Agent ----------------------------
from agents import (
    Agent, Runner, function_tool, OpenAIChatCompletionsModel, RunConfig, set_tracing_disabled, RunContextWrapper, ModelSettings, StopAtTools, FunctionToolResult, ToolsToFinalOutputResult, ModelSettings, SQLiteSession
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
    # Create agent
    agent = Agent(
        name="Assistant",
        instructions="Reply very concisely.",
        model=model,
    )

    # Create a session instance with a session ID
    session = SQLiteSession("conversation_123")

    # First turn
    result = await Runner.run(
        agent,
        "What city is the Golden Gate Bridge in?",
        session=session
    )
    print(result.final_output)  # "San Francisco"

    # Second turn - agent automatically remembers previous context
    result = await Runner.run(
        agent,
        "What state is it in?",
        session=session
    )
    print(result.final_output)  # "California"

    # Also works with synchronous runner
    # result = Runner.run_sync(
    #     agent,
    #     "What's the population?",
    #     session=session
    # )
    # print(result.final_output)  # "Approximately 39 million"
    
asyncio.run(main())

