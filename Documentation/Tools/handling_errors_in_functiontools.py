#---------------------------- Running Agent ----------------------------
from agents import (
    Agent, Runner, function_tool, OpenAIChatCompletionsModel, RunConfig, set_tracing_disabled, FunctionTool, RunContextWrapper, RunResult, ToolCallOutputItem
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
import requests


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

def my_custom_error_function(ctx: RunContextWrapper[Any], error: Exception) -> str:
    """A custom function to provide a user-friendly error message."""
    print(f"A tool call failed with the following error: {error}")
    return "An internal server error occurred. Please try again later."

@function_tool(failure_error_function=my_custom_error_function)
def get_user_profile(id: int) -> str:
    """Fetches a user profile from a mock API.
     This function demonstrates a 'flaky' or failing API call.
    """
    response = requests.get(f"https://dummyjson.com/users/{id}")
    api_result = response.json()
    if response.status_code != 200:
        raise ValueError(f"API call failed with status code {response.status_code}: {api_result.get('message', 'Unknown error')}")
    else:
        if id == 1:
            return "User profile for user_123 successfully retrieved."
        else:
            raise ValueError(f"Could not retrieve profile for user_id: {id}. API returned an error.")

agent = Agent(
    name="ErrorHandlingAgent",
    instructions="An agent that demonstrates error handling in function tools.",
    tools=[get_user_profile],
    model=model,
)

async def main():
    result = await Runner.run(agent, "get user profile respect to id and show all details of user in result", run_config=run_config)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())