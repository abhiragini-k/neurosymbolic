import asyncio
import os
import sys
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.append(os.getcwd())
load_dotenv(".env")

async def clear_cache():
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DATABASE_NAME", "drug_repurposing_db")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    collection = db["drug_disease_evidence"]
    
    result = await collection.delete_many({})
    print(f"Cleared {result.deleted_count} cached evidence records.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(clear_cache())
