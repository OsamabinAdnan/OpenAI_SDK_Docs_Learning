#---------------------------- Running Agent ----------------------------
from agents import (
    Agent, Runner, function_tool, OpenAIChatCompletionsModel, RunConfig, set_tracing_disabled
)
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv
import random
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
)
    
async def main():
    agent = Agent(
        name="Joker",
        instructions="You are a helpful assistant.",
        
    )

    result = Runner.run_streamed(
        agent,
        input="Please tell me 5 jokes.",
        run_config=run_config,
    )

    print("=== Run starting ===")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
    print("=== Run complete ===")


if __name__ == "__main__":
    asyncio.run(main())
