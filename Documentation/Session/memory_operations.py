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
    # model_provider=external_client,
    # model_settings=ModelSettings(
    #     max_tokens=200,
    #     temperature=0.7,
    #     top_p=0.3,
    #     # frequency_penalty=0.2,
    #     presence_penalty=0.2,
    # ),
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
    # ------------------------- Basic Operation -------------------------
    
    session = SQLiteSession("user_123", "conversations.db")

    # Get all items in a session
    items = await session.get_items()

    # Add new items to a session
    new_items = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    await session.add_items(new_items)

    # Remove and return the most recent item
    last_item = await session.pop_item()
    print(last_item)  # {"role": "assistant", "content": "Hi there!"}

    # Clear all items from a session
    await session.clear_session()

    # ------------------------- Using pop_item for corrections -------------------------

    agent = Agent(name="Assistant")
    session = SQLiteSession("correction_example")

# Initial conversation
    result = await Runner.run(
        agent,
        "What's 2 + 2?",
        session=session
    )
    print(f"Agent: {result.final_output}")

    # User wants to correct their question
    assistant_item = await session.pop_item()  # Remove agent's response
    user_item = await session.pop_item()  # Remove user's question

    # Ask a corrected question
    result = await Runner.run(
        agent,
        "What's 2 + 3?",
        session=session
    )
    print(f"Agent: {result.final_output}")
    
asyncio.run(main())


