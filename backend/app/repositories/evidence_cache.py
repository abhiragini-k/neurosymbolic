from datetime import datetime
from typing import Optional, Dict
from app.core.database import db

# This implementation assumes `app.core.database.db` exposes the motor client or database wrapper.
# Based on `analysis.py`, `db` is imported from `app.core.database`.
# `analysis.py` uses `db["jobs"]` which implies `db` is the database object (or behaves like one).

async def get_cached_evidence(drug_id: str, disease_id: str) -> Optional[Dict]:
    """
    Retrieves cached evidence for a drug-disease pair.
    """
    try:
        # Construct _id to match save_evidence
        doc_id = f"{drug_id}::{disease_id}"
        # Access collection via the db wrapper/object
        # Assuming db is a MotorDatabase or similar proxy
        collection = db.get_db()["drug_disease_evidence"]
        return await collection.find_one({"_id": doc_id})
    except Exception as e:
        print(f"Cache read error: {e}")
        return None

async def save_evidence(doc: Dict) -> None:
    """
    Saves evidence to the cache.
    """
    try:
        collection = db.get_db()["drug_disease_evidence"]
        # Use simple replace_one with upsert=True to handle updates/inserts
        await collection.replace_one(
            {"_id": doc["_id"]},
            doc,
            upsert=True
        )
    except Exception as e:
        print(f"Cache write error: {e}")

# Manual Index Creation Instruction:
# Run in MongoDB Shell:
# db.drug_disease_evidence.createIndex(
#   { createdAt: 1 },
#   { expireAfterSeconds: 604800 }
# )
