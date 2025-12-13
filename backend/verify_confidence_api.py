
from fastapi.testclient import TestClient
from app.main import app
import sys
import os

# Ensure backend dir is in path
sys.path.append(os.path.join(os.getcwd(), "backend"))

client = TestClient(app)

def test_confidence_breakdown():
    print("Testing /analysis/confidence-breakdown...")
    
    # Use a known drug/disease pair. Metformin -> Diabetes (or similar)
    # Metformin ID: 6809
    # Diabetes Mellitus Type 2 ID: 3077 (Example, check disease_id_to_name.json if needed, or use names)
    
    # We'll use Names as that's what we implemented support for
    drug = "Metformin"
    disease = "type 2 diabetes mellitus" 

    
    # URL Encode params? TestClient handles it
    try:
        response = client.get(f"/analysis/confidence-breakdown?drug_id={drug}&disease_id={disease}")
        
        if response.status_code == 200:
            print("[OK] API Call Successful!")
            data = response.json()
            print("Response Keys:", data.keys())
            
            # Check structure
            print("Response Keys:", data.keys())
            
            # Check structure
            if "averages" not in data or "normalized" not in data or "details" not in data:
                 print(f"[FAIL] Missing keys. Found: {data.keys()}")
            else:
                 avgs = data['averages']
                 norms = data['normalized']
                 print("\n--- AVERAGES ---")
                 for k, v in avgs.items():
                     print(f"  - {k}: {v}")
                
                 print("\n--- NORMALIZED ---")
                 for k, v in norms.items():
                     print(f"  - {k}: {v}")
                     
                 details = data['details']
                 print("\n--- DETAILS (Sample) ---")
                 if details['pathways']:
                     print(f"  - First Pathway: {details['pathways'][0]['path']}")
                 
                 if avgs['final_confidence'] > 0:
                     print(f"\nVerification Passed. Final Score: {avgs['final_confidence']}%")
                 else:
                     print("\n[WARN] Final confidence is 0.")

            
    except Exception as e:
        print(f"[FAIL] Exception during test: {e}")


if __name__ == "__main__":
    test_confidence_breakdown()
