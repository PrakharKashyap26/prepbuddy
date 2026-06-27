import sys
import os

# Add backend subdirectory at the top of the search path for resolving imports
backend_path = os.path.join(os.path.dirname(__file__), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Explicitly import from the backend namespace to avoid naming collisions with the root main.py
from backend.main import app
