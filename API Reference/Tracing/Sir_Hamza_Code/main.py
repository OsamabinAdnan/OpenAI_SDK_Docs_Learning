import os
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, trace, set_tracing_export_api_key, enable_verbose_stdout_logging
from openai import AsyncOpenAI
from rich import print

load_dotenv()

enable_verbose_stdout_logging()

tracking_api_key = os.environ["OPENAI_API_KEY"]
set_tracing_export_api_key(tracking_api_key)

MODEL_NAME = "gemini-2.5-flash" # which LLM model will agent use

GEMINI_API_KEY= os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY is not set")

BASE_URL = os.getenv("BASE_URL")
if not BASE_URL:
    raise Exception("BASE_URL is not set")


# external_client is the connection that allows us to talk with Gemini API
external_client = AsyncOpenAI(
        api_key = GEMINI_API_KEY,
        base_url = BASE_URL, #it is Gemini api endpoint bcx we are using Gemini LLM in OpenAI Agents framework
)

model = OpenAIChatCompletionsModel(
        model = MODEL_NAME,
        openai_client=external_client, #connect external cient with OpenAI client
)

faq_agent= Agent(
    name= "FAQ Agent",
    instructions="Answer only product-related frequently asked questions.",
    model=model
)

support_agent = Agent(
    name = "Support Agent",
    instructions="Politely tell the user that only product-related queries are allowed.",
    model=model
)

# Trace Example:

#Trace 1 - Simple Trace (Single run)

print("\nSingle Trace Response")
print("=" * 30)
with trace("Single Trace Workflow"):
    faq_result = Runner.run_sync(
        faq_agent, 
        "What is Refund policy"
    )
    print("FAQ Response: ",faq_result.final_output)
    #this will create agent span and generation span in one trace


# Trace 2- Multi Tracing (Higher Level Traces)
print("\nMulti Trace Response")
print("=" * 30)
with trace("Multi Trace Workflow"):
    
    #first span
    faq_result = Runner.run_sync(faq_agent, "Tell me the joke")
    print("FAQ Response: ",faq_result.final_output)

    #second span
    support_result = Runner.run_sync(support_agent, f" User Asked {faq_result.final_output}")
    print("Support Response: ",support_result.final_output)    
    #it will create two individual agent span and generation in one trace