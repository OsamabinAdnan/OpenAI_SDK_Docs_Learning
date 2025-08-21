#---------------------------- Running Agent ----------------------------
from agents import (
    Agent, Runner, function_tool, OpenAIChatCompletionsModel, RunConfig, set_tracing_disabled, FunctionTool, RunContextWrapper
)
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv
import random
import os
from rich import print
from dataclasses import dataclass
from pydantic import BaseModel
from typing import Any, List, TypedDict
import asyncio
import json


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

# ---------------------------- Agent as a tool ----------------------------

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You translate the user's message to Spanish",
    model=model,
)

french_agent = Agent(
    name="French agent",
    instructions="You translate the user's message to French",
    model=model,
)

#---------------------------- Customizing tool-agents ----------------------------

# The agent.as_tool function is a convenience method to make it easy to turn an agent into a tool. It doesn't support all configuration though; for example, you can't set max_turns. For advanced use cases, use Runner.run directly in your tool implementation:

@function_tool
async def german_agent() -> str:
    """A tool that runs the agent with custom configs"""

    agent = Agent(
        name="My agent",
        instructions="You will convert the user's message to German.",
        model=model
    )

    result = await Runner.run(
        agent,
        input="Say 'Hello, how are you?' in German.",
        max_turns=5,
        run_config=run_config,
    )

    return str(result.final_output)

# ----------------------------- Orchestrator agent (main agent) ----------------------------
orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "You are a translation agent. You use the tools given to you to translate."
        "If asked for multiple translations, you call the relevant tools."
    ),
    tools = [
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate the user's message to Spanish",
        ),
        french_agent.as_tool(
            tool_name="translate_to_french",
            tool_description="Translate the user's message to French",
        ),
        german_agent,
    ]
)

async def main():
    result = await Runner.run(
        starting_agent=orchestrator_agent,
        input= "Say 'Hello, how are you?' in German.",
        run_config=run_config,
    )

    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())