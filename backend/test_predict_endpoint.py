import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import utils
from app.services import pipeline

def test_predict():
    print("Testing /predict/drug logic...")
    
    # 1. Test Utils
    print("Loading mappings...")
    utils.load_mappings()
    
    drug_name = "Metformin"
    print(f"Looking up ID for '{drug_name}'...")
    drug_id = utils.drug_name_to_id(drug_name)
    print(f"Found ID: {drug_id}")
    
    if not drug_id:
        print("❌ Drug not found!")
        return

    # 2. Test Pipeline
    print(f"Running RGCN for ID {drug_id}...")
    try:
        predictions = pipeline.run_rgcn(drug_id, top_k=5)
        print("Predictions:")
        for p in predictions:
            d_name = utils.disease_id_to_name(p['disease_id'])
            print(f" - {d_name} ({p['disease_id']}): {p['score']}")
        print("✅ Success!")
    except Exception as e:
        print(f"❌ Error in run_rgcn: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_predict()
