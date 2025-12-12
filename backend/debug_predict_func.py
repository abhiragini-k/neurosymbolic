import sys
import os
import asyncio
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv(".env")

from app.routers import predict

print(f"Function object: {predict.get_disease_candidates}")
print(f"Type of function: {type(predict.get_disease_candidates)}")

try:
    coro = predict.get_disease_candidates(1, 10)
    print(f"Result of call: {coro}")
    print(f"Type of result: {type(coro)}")
    
    if coro is None:
        print("❌ Function returned None! It should return a coroutine.")
    else:
        print("✅ Function returned something (presumably coroutine).")
        # We won't await it here to avoid the complexity of the previous failure, just checking the type.
        # But if it is a coroutine, we should close it to avoid warnings.
        if asyncio.iscoroutine(coro):
            coro.close()

except Exception as e:
    print(f"❌ Error calling function: {e}")
