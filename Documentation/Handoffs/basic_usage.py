from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel, RunConfig, set_tracing_disabled, handoff
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

billing_agent = Agent(
    name="Billing agent",
    instructions="You are a billing agent. You will handle billing-related queries.",
    model=model,
)
refund_agent = Agent(
    name="Refund agent",
    instructions="You are a refund agent. You will handle refund-related queries.",
    model=model,
)

triage_agent = Agent(
    name="Triage agent",
    instructions="You are a triage agent. You will determine whether to hand off to the billing or refund agent.",
    model=model,
    handoffs=[billing_agent, handoff(agent=refund_agent)]
)

result = Runner.run_sync(
    starting_agent=triage_agent,
    input="I want to request a refund for my last purchase.",
    run_config=run_config,
)

print(f"Result: {result.final_output}")