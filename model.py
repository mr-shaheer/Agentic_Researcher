import os
from agents import AsyncOpenAI, OpenAIChatCompletionsModel
from dotenv import load_dotenv, find_dotenv

load_dotenv()

external_client = AsyncOpenAI(
    api_key = os.getenv("GEMINI_API_KEY"),
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/",
)

high_model = OpenAIChatCompletionsModel(
    model = "gemini-2.5-flash",
    openai_client=external_client
)

low_model = OpenAIChatCompletionsModel(
    model = "gemini-2.5-flash-lite",
    openai_client = external_client
)

