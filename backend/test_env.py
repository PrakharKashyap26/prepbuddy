import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fallback to parent directory if running from backend folder
if not os.getenv("GEMINI_API_KEY"):
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

def mask_key(val: str) -> str:
    if not val:
        return "Not Set"
    if len(val) <= 8:
        return "****"
    return f"{val[:4]}********{val[-4:]}"

keys_to_test = ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_CSE_ID", "SECRET_KEY"]

for key in keys_to_test:
    val = os.getenv(key)
    if val:
        print(f"{key} loaded: {mask_key(val)}")
    else:
        print(f"{key} failed to load: Not Found")
