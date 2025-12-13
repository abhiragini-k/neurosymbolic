import requests
import json
import urllib.parse

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url):
    print(f"Testing {name} ({url})...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"✅ {name} Success")
            return True
        else:
            print(f"❌ {name} Failed: {response.status_code}")
            print(response.text[:200]) # Print first 200 chars
            return False
    except Exception as e:
        print(f"❌ {name} Error: {e}")
        return False

if __name__ == "__main__":
    drug = "Metformin"
    disease = "type 2 diabetes mellitus"
    
    # Test new /api prefixed routes
    test_endpoint("Pathway Influence", f"{BASE_URL}/api/explainability/pathway?drug_id={drug}&disease_id={disease}")
    test_endpoint("Gene Match", f"{BASE_URL}/api/explainability/gene-match?drug_id={drug}&disease_id={disease}")
