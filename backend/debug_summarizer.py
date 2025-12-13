import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv(".env")

from app.services import pubmed_client, evidence_summarizer

async def debug_summarizer():
    # Test Data: Rivastigmine (Drug) -> Alzheimer's disease (Disease)
    # These are known to have significant literature.
    drug_name = "Rivastigmine"
    disease_name = "Alzheimer's disease"
    
    print(f"--- Debugging Summarizer for: {drug_name} vs {disease_name} ---")

    # 1. Fetch Papers
    print("1. Fetching papers from PubMed...")
    papers = await pubmed_client.fetch_papers(drug_name, disease_name)
    print(f"   Found {len(papers)} papers.")
    
    if not papers:
        print("[X] No papers found. Summarizer will not be called in production flow.")
        return

    # 2. Call Summarizer
    print("2. Calling Summarizer...")
    try:
        summary = await evidence_summarizer.summarize_evidence(drug_name, disease_name, papers)
        print("\n[OK] Summarizer Result:")
        print(f"Overall Summary: {summary.get('overall_summary')}")
        print(f"Points: {summary.get('points')}")
        
        if summary.get('overall_summary') == "Evidence summary temporarily unavailable.":
             print("\n[FAIL] FALLBACK TRIGGERED. Likely Causes:")
             print("   - OPENAI_API_KEY missing or invalid.")
             print("   - Network issue reaching OpenAI.")
             print("   - Exception in evidence_summarizer code.")
        else:
             print("\n[SUCCESS] Real summary generated.")
             
    except Exception as e:
        print(f"[X] Exception calling summarizer: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(debug_summarizer())
