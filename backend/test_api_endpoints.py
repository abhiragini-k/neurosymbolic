import sys
import os
from fastapi.testclient import TestClient

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)

def test_explainability_endpoints():
    print("\n--- Testing Explainability API Endpoints ---")
    
    drug_id = "0"
    disease_id = "0"

    # 1. Test Pathway Influence
    print("\n[GET] /explainability/pathway")
    response = client.get(f"/explainability/pathway?drug_id={drug_id}&disease_id={disease_id}")
    
    if response.status_code == 200:
        data = response.json()
        print("Success: 200 OK")
        if "pathway_influence" in data:
            items = data["pathway_influence"]
            print(f"Items returned: {len(items)}")
            if len(items) > 0:
                print(f"Sample Item: {items[0]}")
        else:
            print("Error: 'pathway_influence' key missing in response.")
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)

    # 2. Test Gene Match
    print("\n[GET] /explainability/gene-match")
    response = client.get(f"/explainability/gene-match?drug_id={drug_id}&disease_id={disease_id}")
    
    if response.status_code == 200:
        data = response.json()
        print("Success: 200 OK")
        if "gene_matches" in data:
            items = data["gene_matches"]
            print(f"Items returned: {len(items)}")
            if len(items) > 0:
                print(f"Sample Item: {items[0]}")
        else:
            print("Error: 'gene_matches' key missing in response.")
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    try:
        test_explainability_endpoints()
    except Exception as e:
        print(f"TEST FAILED: {e}")
