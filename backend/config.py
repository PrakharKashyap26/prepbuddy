import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fallback to loading the parent directory's .env file if run from the backend directory
if not os.getenv("GEMINI_API_KEY"):
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Fetch configuration variables using os.getenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
SECRET_KEY = os.getenv("SECRET_KEY")

# Validate required variables
if not GEMINI_API_KEY:
    raise ValueError(
        "Configuration Error: GEMINI_API_KEY is missing from the environment variables. "
        "Please specify it in your .env file."
    )
