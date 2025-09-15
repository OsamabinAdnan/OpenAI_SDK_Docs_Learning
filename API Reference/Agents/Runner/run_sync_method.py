import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, RunContextWrapper, Runner, OpenAIChatCompletionsModel, enable_verbose_stdout_logging, function_tool, handoff
from openai import AsyncOpenAI
from rich import print

load_dotenv()
# enable_verbose_stdout_logging()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise Exception("GEMINI_API_KEY is not set")


my_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model_25 = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=my_client,
)

model_20 = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=my_client,
)

# Tools
@function_tool
def get_weather(city:str):
    return f"The weather in {city} is sunny"

@function_tool
def add_two_numbers(a:int, b:int):
    sum = a + b
    return f"The sum of {a} and {b} is {sum}"

# Python Agent
python_agent = Agent(
    name="Python_Agent",
    instructions="""
        You are a Python agent.
    """,
    model=model_20,
    handoff_description="""
        You are expert in python programming language.
        - You can answer questions related to python programming language only.
    """,
)

python_agent_hanoff = handoff(
    agent=python_agent,
)


main_agent = Agent(
    name="Main Agent",
    instructions="""
        You are helpful assistant.
    """,
    model=model_25,
    tools=[get_weather, add_two_numbers],
    handoffs=[python_agent_hanoff],
)
result = Runner.run_sync(
    main_agent,
    "What is OOPs in python! in 200 words",
) # -> RunResult
print(f"\n{result.final_output}\n")

