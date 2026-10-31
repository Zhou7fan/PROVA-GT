"""Central configuration for PROVA-GT backend services.

All API keys are read from environment variables (or a local .env file).
Copy .env.example to .env and fill in your own keys before starting the services.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def require_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Environment variable {name} is not set. "
            "Copy .env.example to .env in the backend directory and fill in your API keys."
        )
    return value
