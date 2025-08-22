from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel, RunConfig, set_tracing_disabled, handoff, RunContextWrapper
from openai import AsyncOpenAI
from agents.extensions import handoff_filters
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

agent = Agent(
    name="FAQ agent", 
    instructions="Answer customer support queries based on provided FAQ data.",  
    model=model
)

handoff_obj = handoff(
    agent=agent,
    input_filter=handoff_filters.remove_all_tools,
)

main_agent = Agent(
    name="Main agent",
    instructions="You are a helpful assistant. You will answer questions and escalate to the FAQ agent when necessary.",
    model=model,
    handoffs=[handoff_obj],
)

result = Runner.run_sync(
    starting_agent=main_agent,
    input="What are your expertise areas?",
    run_config=run_config,
)

print(f"Result: {result.final_output}")
