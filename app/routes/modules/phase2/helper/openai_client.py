import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(override=True)

# Global client variable
client = None

def get_openai_client():
    """Get OpenAI client with lazy initialization"""
    global client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        client = OpenAI(api_key=api_key)
    return client
