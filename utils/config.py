import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_config(key: str, default: str = None) -> str:
    """
        KEY = get_config('KEY','default') <- set KEY in .env file
    """
    return os.getenv(key, default)
