import requests
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(path, params=None):
    url = f"{BASE_URL}{path}"
    try:
        print(f"Testing {url}...")
        response = requests.get(url, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
            # print(response.json())
        else:
            print(f"Failed: {response.text[:200]}")
        return response.status_code
    except Exception as e:
        print(f"Error: {e}")
        return -1

def main():
    print("Verifying API Endpoints...")
    
    # 1. Test Root
    test_endpoint("/")
    
    # 2. Test Confidence Breakdown
    # /api/analysis/confidence-breakdown
    test_endpoint("/api/analysis/confidence-breakdown", {"drug_id": "Metformin", "disease_id": "type 2 diabetes mellitus"})
    
    # 3. Test Explainability Pathway
    # /api/explainability/pathway
    test_endpoint("/api/explainability/pathway", {"drug_id": "Metformin", "disease_id": "type 2 diabetes mellitus"})
    
    # 4. Test Explainability Gene Match
    # /api/explainability/gene-match
    test_endpoint("/api/explainability/gene-match", {"drug_id": "Metformin", "disease_id": "type 2 diabetes mellitus"})

if __name__ == "__main__":
    main()
