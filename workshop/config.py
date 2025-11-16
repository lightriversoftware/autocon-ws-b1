import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()


deployment = os.getenv("OPENAI_DEPLOYMENT")
endpoint = os.getenv("OPENAI_ENDPOINT")

llm_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=endpoint,
)
GENERATIVE_MODEL = deployment
