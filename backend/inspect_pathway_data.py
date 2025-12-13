import requests
import json
import urllib.parse

BASE_URL = "http://localhost:8000"

def inspect_pathway_data(drug, disease):
    url = f"{BASE_URL}/api/explainability/pathway?drug_id={urllib.parse.quote(drug)}&disease_id={urllib.parse.quote(disease)}"
    print(f"Fetching: {url}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("Response Keys:", data.keys())
            if "pathway_influence" in data:
                items = data["pathway_influence"]
                print(f"Count: {len(items)}")
                print("Top 5 Items:")
                for item in items[:5]:
                    print(item)
            else:
                print("❌ 'pathway_influence' key missing!")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text[:200])
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_pathway_data("Metformin", "type 2 diabetes mellitus")
