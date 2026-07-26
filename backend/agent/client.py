import os

from agents import OpenAIChatCompletionsModel, set_tracing_disabled
from dotenv import load_dotenv
from openai import AsyncOpenAI

DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"


def create_deepseek_model() -> OpenAIChatCompletionsModel:
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        raise ValueError("没有找到 DEEPSEEK_API_KEY，请检查 backend/.env 文件")

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=os.getenv(
            "DEEPSEEK_BASE_URL",
            DEFAULT_DEEPSEEK_BASE_URL,
        ),
    )

    return OpenAIChatCompletionsModel(
        model=os.getenv(
            "DEEPSEEK_MODEL",
            DEFAULT_DEEPSEEK_MODEL,
        ),
        openai_client=client,
    )


set_tracing_disabled(True)
