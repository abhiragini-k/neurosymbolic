import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load env from backend/.env
# Assuming this script is run from backend/ directory or we point it there
load_dotenv(".env")

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "drug_repurposing_db")

print(f"Connecting to {MONGODB_URL}...")
print(f"Database: {DATABASE_NAME}")

async def create_ttl_index():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    collection_name = "drug_disease_evidence"
    collection = db[collection_name]

    print(f"Creating TTL index on '{collection_name}'...")
    
    try:
        # Create index on createdAt field, expire after 7 days (604800 seconds)
        result = await collection.create_index(
            "createdAt",
            expireAfterSeconds=604800,
            name="evidence_ttl_index"
        )
        print(f"✅ Success! Index created: {result}")
    except Exception as e:
        print(f"❌ Error creating index: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_ttl_index())
