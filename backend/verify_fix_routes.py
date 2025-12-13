import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url):
    print(f"Testing {name} ({url})...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"✅ {name} Success")
            # print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ {name} Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ {name} Error: {e}")
        return False

if __name__ == "__main__":
    # Use known valid IDs (e.g. from previous context or defaults)
    # Assuming 0 and 0 are valid for testing
    drug_id = "0" 
    disease_id = "0"
    
    test_endpoint("Pathway Influence", f"{BASE_URL}/explainability/pathway?drug_id={drug_id}&disease_id={disease_id}")
    test_endpoint("Gene Match", f"{BASE_URL}/explainability/gene-match?drug_id={drug_id}&disease_id={disease_id}")
    test_endpoint("Confidence Breakdown", f"{BASE_URL}/analysis/confidence-breakdown?drug_id={drug_id}&disease_id={disease_id}")
