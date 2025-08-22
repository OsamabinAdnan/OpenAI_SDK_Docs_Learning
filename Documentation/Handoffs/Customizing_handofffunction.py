from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel, RunConfig, set_tracing_disabled, handoff, RunContextWrapper
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
from rich import print
from dataclasses import dataclass
from pydantic import BaseModel
from typing import Any, List

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

run_config = RunConfig(
    model=model,
    tracing_disabled=True,
)

def on_handoff(ctx:RunContextWrapper[None]):
    print(f"Handoff called!")

agent = Agent(
    name="Custom handoff agent",
    instructions="You are a custom handoff agent. You will demonstrate a custom handoff function.",
    model=model,
)

handoff_obj = handoff(
    agent=agent,
    on_handoff=on_handoff,
    tool_name_override="custom_handoff_tool",
    tool_description_override="A custom handoff tool that demonstrates a custom handoff function.",
)

result = Runner.run_sync(
    starting_agent=agent,
    input="What are your expertise areas?",
    run_config=run_config,
)

print(f"Result: {result.final_output}")
