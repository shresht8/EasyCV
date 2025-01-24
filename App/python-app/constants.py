import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get PY_ENV from environment variables, default to 'local' if not set
PY_ENV = os.getenv("PY_ENV", "local")
LATEX_API_URL = os.getenv("LATEX_API_URL")

# Add other environment variables here as needed
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Add more variables as needed
