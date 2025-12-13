import asyncio
import os
import sys
from dotenv import load_dotenv

# Setup path
sys.path.append(os.getcwd())

# Load Env
load_dotenv(".env")

from app.core.database import db
from app.routers import predict
from app.services.mapping_service import mapping_service

async def test_pipeline():
    print("--- Starting Pipeline Verification ---")
    
    # 1. Connect to DB
    print("1. Connecting to MongoDB...")
    db.connect()
    
    # 2. Check if matrix loaded in predict.py
    if predict.scores is None:
        print("❌ Prediction matrix not loaded in predict.py. Check file paths.")
        return

    print("2. Prediction matrix metadata:")
    print(f"   Shape: {predict.scores.shape}")
    
    # 3. Simulate Request
    # We'll try to get candidates for disease_id=1 (assuming it exists and has range)
    # If 1 is out of range, we'll try 0.
    test_disease_id = 0 
    if test_disease_id >= predict.scores.shape[1]:
        print(f"❌ Test disease ID {test_disease_id} out of range.")
        return

    print(f"3. Calling get_disease_candidates(disease_id={test_disease_id})...")
    try:
        # This will trigger: Cache Check -> PubMed -> Summarizer -> Cache Save
        response = await predict.get_disease_candidates(disease_id=test_disease_id, top_k=2)
        
        print("\n✅ API Response Received!")
        print(f"   Disease: {response['disease_name']}")
        print(f"   Reviewing Top Candidate:")
        
        if response['candidates']:
            cand = response['candidates'][0]
            print(f"   - Drug: {cand['drug_name']}")
            print(f"   - Score: {cand['score']}")
            print(f"   - Papers Found: {len(cand['papers'])}")
            print(f"   - Summary: {cand['summary'].get('overall_summary')[:100]}...")
            
            if cand['summary'].get('overall_summary') == "Evidence summary temporarily unavailable.":
                print("\n⚠️ Note: Summarizer returned fallback. Check OPENAI_API_KEY if this was unexpected.")
            else:
                print("\n✨ Summarizer returned real content!")
        else:
            print("   No candidates returned (unexpected for top_k=2).")

    except Exception as e:
        print(f"❌ Error during pipeline execution: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_pipeline())
