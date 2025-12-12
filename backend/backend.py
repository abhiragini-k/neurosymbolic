import numpy as np
from fastapi import FastAPI
import json
import os

app = FastAPI()

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Navigate up to neurosymbolic, then down to R-GCN/R-GCN-MODEL
MODEL_DIR = os.path.join(os.path.dirname(BASE_DIR), "R-GCN", "R-GCN-MODEL")
PREDICTION_MATRIX_PATH = os.path.join(MODEL_DIR, "compound_disease_predictions.npy")

# Load the prediction matrix once
print(f"Loading prediction matrix from {PREDICTION_MATRIX_PATH}...")
try:
    scores = np.load(PREDICTION_MATRIX_PATH, allow_pickle=True).astype(float)
    print(f"Matrix loaded. Shape: {scores.shape}")
except FileNotFoundError:
    print(f"Error: {PREDICTION_MATRIX_PATH} not found!")
    scores = np.zeros((1, 1)) # Fallback

# Load mappings (optional)
print("Loading mappings...")
try:
    compound_names = json.load(open("compound_id_to_name.json"))
    disease_names = json.load(open("disease_id_to_name.json"))
    print("Mappings loaded.")
except FileNotFoundError:
    print("Warning: JSON mappings not found.")
    compound_names = {}
    disease_names = {}

# 1️⃣ API — Predict top diseases for a compound
@app.get("/predict/drug/{compound_id}")
def predict_drug(compound_id: int, top_k: int = 10):
    if compound_id >= len(scores):
        return {"error": f"Compound ID {compound_id} out of range (max {len(scores)-1})"}
        
    compound_scores = scores[compound_id]
    top_indices = compound_scores.argsort()[-top_k:][::-1]

    results = []
    for rank, disease_id in enumerate(top_indices, 1):
        # Convert numpy types to native python types for JSON serialization
        results.append({
            "compound_id": compound_id,
            "compound_name": compound_names.get(str(compound_id), str(compound_id)),
            "disease_id": int(disease_id),
            "disease_name": disease_names.get(str(disease_id), str(disease_id)),
            "score": float(compound_scores[disease_id]),
        })
    
    return {"predictions": results}

# 2️⃣ API — Predict single pair score
@app.get("/predict/pair/{compound_id}/{disease_id}")
def predict_pair(compound_id: int, disease_id: int):
    # Check bounds
    if compound_id >= scores.shape[0]:
        return {"error": f"Compound ID {compound_id} out of range"}
    if disease_id >= scores.shape[1]:
        return {"error": f"Disease ID {disease_id} out of range"}

    return {
        "compound_id": compound_id,
        "compound_name": compound_names.get(str(compound_id), str(compound_id)),
        "disease_id": disease_id,
        "disease_name": disease_names.get(str(disease_id), str(disease_id)),
        "score": float(scores[compound_id, disease_id])
    }

# 3️⃣ API — Predict by drug name (Bonus)
@app.get("/predict/drug-name/{drug_name}")
def predict_drug_by_name(drug_name: str, top_k: int = 10):
    # Invert mapping to find ID
    target_id = None
    for cid, name in compound_names.items():
        if name.lower() == drug_name.lower():
            target_id = int(cid)
            break
            
    if target_id is None:
        return {"error": f"Drug '{drug_name}' not found in mapping"}
        
    return predict_drug(target_id, top_k)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
