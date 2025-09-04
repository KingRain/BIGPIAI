# cv_processor/utils/env_utils.py
"""
Environment variable loading utilities.
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    load_dotenv = None


def load_env_from_file(env_file: str = ".env") -> None:
    """Load environment variables from .env file."""
    if not DOTENV_AVAILABLE:
        print("⚠️  python-dotenv not installed, skipping .env file loading")
        return
        
    env_path = Path(env_file)
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded environment variables from {env_file}")
    else:
        print(f"⚠️  Environment file {env_file} not found")


def get_env_var(var_name: str, default: str = None, required: bool = False) -> str:
    """Get environment variable with optional default and required check."""
    value = os.getenv(var_name, default)
    if required and not value:
        raise ValueError(f"Required environment variable {var_name} not set")
    return value


def setup_env_vars() -> None:
    """Set up default environment variables if not already set."""
    defaults = {
        "AI_PROVIDER": "gemini",
        "MODEL_NAME": "gemini-1.5-flash",
        "CONCURRENCY": "3"
    }
    
    for var, default_val in defaults.items():
        if not os.getenv(var):
            os.environ[var] = default_val
            print(f"✓ Set default {var}={default_val}")


def validate_required_env_vars() -> bool:
    """Validate that all required environment variables are set."""
    required_vars = ["GEMINI_API_KEY"]
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing required environment variables: {missing}")
        return False
    
    print("✓ All required environment variables are set")
    return True
