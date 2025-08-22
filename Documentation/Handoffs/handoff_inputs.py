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

class EscalationData(BaseModel):
    reason: str

async def on_handoff(ctx: RunContextWrapper[None], input_data: EscalationData):
    print(f"Escalation agent called with reason: {input_data.reason}")

agent = Agent(
    name="Escalation agent", 
    instructions="Handle customer support queries and escalate when necessary.",  
    model=model
)

handoff_obj = handoff(
    agent=agent,
    on_handoff=on_handoff,
    input_type=EscalationData,
)

result = Runner.run_sync(
    starting_agent=agent,
    input="What are your expertise areas?",
    run_config=run_config,
)

print(f"Result: {result.final_output}")