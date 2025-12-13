import requests
import json
import urllib.parse

BASE_URL = "http://localhost:8000"

def test_analysis(drug, disease):
    # Encode URL components
    drug_enc = urllib.parse.quote(drug)
    disease_enc = urllib.parse.quote(disease)
    url = f"{BASE_URL}/api/analysis/{drug_enc}/{disease_enc}"
    
    print(f"Testing Analysis: {drug} -> {disease}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ Success")
            data = response.json()
            print(f"   Compound: {data.get('compound_name')}")
            print(f"   Disease: {data.get('disease_name')}")
            print(f"   Neural Score: {data.get('neural_score')}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Test with names as reported in the issue
    test_analysis("Metformin", "type 2 diabetes mellitus")
    
    # Test with IDs (as strings)
    test_analysis("0", "0")
