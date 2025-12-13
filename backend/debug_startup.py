import sys
import os
import traceback

# Add the current directory to sys.path so we can import app
sys.path.append(os.getcwd())

print("Attempting to import app.main...")
try:
    from app import main
    print("Successfully imported app.main")
except Exception:
    print("Failed to import app.main")
    traceback.print_exc()
