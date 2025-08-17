from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel, RunConfig, set_tracing_disabled, RunContextWrapper, ModelSettings, StopAtTools, FunctionToolResult, ToolsToFinalOutputResult
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
from rich import print
from dataclasses import dataclass
from pydantic import BaseModel
from typing import Any, List

load_dotenv()

set_tracing_disabled(True)

# Dynamic instructions function
def dynamic_function(ctx:RunContextWrapper, agent:Agent):
    return "You are helpful assistant"


# ToolsToFinalOutputFunction
@function_tool
def get_weather(city: str) -> str:
    """Returns weather info for the specified city."""
    return f"The weather in {city} is sunny"

def custom_tool_handle(context:RunContextWrapper[Any], tool_result:List[FunctionToolResult]) -> ToolsToFinalOutputResult:
    """Processes tool results to decide final output."""
    for result in tool_result:
        if result.output and "sunny" in result.output:
            return ToolsToFinalOutputResult(
                is_final_output=True,
                final_output=f"Final Weather: {result.output}",
            )
    
    return ToolsToFinalOutputResult(
        is_final_output=False,
        final_output=None,
    )

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

# Context
@dataclass
class UserContext:
    name: str
    uid: str
    is_pro_user:bool

user_context_agent = Agent[UserContext](
    name="user_context_agent",
    instructions="Provide user context",
)

# Output types
class CalenderEvent(BaseModel):
    name:str
    date:str
    participants:list[str]

calender_agent = Agent(
    name="calender_agent",
    instructions="Extract calendar events from text",
    output_type=CalenderEvent
)

# Weather Agent | using function tool and dynamic instructions function
weather_agent = Agent(
    name="my_agent",
    instructions=dynamic_function,
    tools=[get_weather],
    model=model,
    model_settings=ModelSettings(
        tool_choice="get_weather", # Forcing tool use
    ),

    # The tool_use_behavior parameter in the Agent configuration controls how tool outputs are handled: - "run_llm_again": The default. Tools are run, and the LLM processes the results to produce a final response. - "stop_on_first_tool": The output of the first tool call is used as the final response, without further LLM processing.
    tool_use_behavior="stop_on_first_tool",

    # StopAtTools(stop_at_tool_names=[...]): Stops if any specified tool is called, using its output as the final response.
    # tool_use_behavior=StopAtTools(stop_at_tool_names=["get_weather"])
)

# Basic configuration
main_agent = Agent(
    name="main_agent",
    instructions="""
        You are main agent, delegate work to experts agent based on the user query.
        For weather related queries, use weather_agent.
        For calendar related queries, use calender_agent.
        For user context, use user_context_agent.
        """,
    handoffs=[
        weather_agent,
        user_context_agent,
        calender_agent
    ],
)

# Cloning/copying agents

# By using the clone() method on an agent, you can duplicate an Agent, and optionally change any properties you like.

# pirate_agent = Agent(
#     name="Pirate",
#     instructions="Write like a pirate",
#     model="o3-mini",
# )

# robot_agent = pirate_agent.clone(
#     name="Robot",
#     instructions="Write like a robot",
# )


result = Runner.run_sync(
    main_agent,
    input= "What is the weather in San Francisco today?",
    run_config=run_config,
)

print(result.final_output)
print(result.last_agent)
