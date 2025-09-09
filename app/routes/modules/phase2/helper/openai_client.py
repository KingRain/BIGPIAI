import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
client = OpenAI(api_key=api_key)
