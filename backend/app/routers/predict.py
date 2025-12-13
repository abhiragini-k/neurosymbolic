from fastapi import APIRouter, HTTPException, Query
import numpy as np
import os
import json
from typing import List, Dict, Any
from pydantic import BaseModel

router = APIRouter()

# Global variables to verify caching
# We will load these at module level for simplicity, similar to the standalone script.
# In a larger app, this might go into a service class or lifespan state.

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Navigate up to neurosymbolic, then down to R-GCN-MODEL
# d:\codered\neurosymbolic\R-GCN-MODEL
MODEL_DIR = os.path.join(os.path.dirname(BASE_DIR), "R-GCN-MODEL")
PREDICTION_MATRIX_PATH = os.path.join(MODEL_DIR, "compound_disease_predictions.npy")

COMPOUND_MAPPING_PATH = os.path.join(BASE_DIR, "compound_id_to_name.json")
DISEASE_MAPPING_PATH = os.path.join(BASE_DIR, "disease_id_to_name.json")

print(f"Loading Logic initialized in predict.py")

# Lazy loading or immediate loading?
# The standalone script loaded immediately. Let's do that for consistency with the requested "one-time load".
try:
    print(f"Loading prediction matrix from {PREDICTION_MATRIX_PATH}...")
    scores = np.load(PREDICTION_MATRIX_PATH, allow_pickle=True).astype(float)
    print(f"Matrix loaded. Shape: {scores.shape}")
except FileNotFoundError:
    print(f"Error: {PREDICTION_MATRIX_PATH} not found! predictions will fail.")
    scores = None

try:
    compound_names = json.load(open(COMPOUND_MAPPING_PATH))
    disease_names = json.load(open(DISEASE_MAPPING_PATH))
    
    # ---------------------------------------------------------
    # TRANSLATION LAYER: Human-Readable <--> Model ID
    # ---------------------------------------------------------
    # Pre-calculate reverse mapping for O(1) lookup
    # Frontend sends "Drug Name" -> We find "Compound ID"
    name_to_id = {name.lower().strip(): int(cid) for cid, name in compound_names.items()}
    print(f"Loaded {len(name_to_id)} compounds for name resolution.")
    
except FileNotFoundError:
    print("Warning: JSON mappings not found in backend root.")
    compound_names = {}
    disease_names = {}
    name_to_id = {}

@router.get("/drug/{compound_id}", summary="Predict top diseases for a drug ID")
def predict_drug(compound_id: int, top_k: int = 10):
    if scores is None:
        raise HTTPException(status_code=500, detail="Prediction matrix not loaded")
    
    if compound_id >= len(scores):
        raise HTTPException(status_code=404, detail=f"Compound ID {compound_id} out of range")
        
    compound_scores = scores[compound_id]
    top_indices = compound_scores.argsort()[-top_k:][::-1]

    results = []
    for rank, disease_id in enumerate(top_indices, 1):
        results.append({
            "compound_id": compound_id,
            "compound_name": compound_names.get(str(compound_id), str(compound_id)),
            "disease_id": int(disease_id),
            "disease_name": disease_names.get(str(disease_id), str(disease_id)),
            "score": float(compound_scores[disease_id]),
        })
    
    return {"predictions": results}

@router.get("/pair/{compound_id}/{disease_id}", summary="Get score for a specific pair")
def predict_pair(compound_id: int, disease_id: int):
    if scores is None:
        raise HTTPException(status_code=500, detail="Prediction matrix not loaded")

    if compound_id >= scores.shape[0]:
        raise HTTPException(status_code=404, detail="Compound ID out of range")
    if disease_id >= scores.shape[1]:
        raise HTTPException(status_code=404, detail="Disease ID out of range")

    return {
        "compound_id": compound_id,
        "compound_name": compound_names.get(str(compound_id), str(compound_id)),
        "disease_id": disease_id,
        "disease_name": disease_names.get(str(disease_id), str(disease_id)),
        "score": float(scores[compound_id, disease_id])
    }

@router.get("/drug-name/{drug_name}", summary="Predict by drug name")
def predict_drug_by_name(drug_name: str, top_k: int = 10):
    """
    Full Flow for Frontend:
    1. Frontend sends 'drug_name' (e.g. 'Aspirin')
    2. Backend converts Name -> ID (using name_to_id map)
    3. Backend queries Model Matrix (using ID)
    4. Backend converts Result IDs -> Disease Names
    5. Frontend receives human-readable JSON
    """
    clean_name = drug_name.lower().strip()
    
    # Step 2: Convert Name -> ID
    if clean_name not in name_to_id:
        raise HTTPException(status_code=404, detail=f"Drug '{drug_name}' not found in knowledge graph.")
    
    target_id = name_to_id[clean_name]
    
    # Step 3, 4, 5: Predict and format
    return predict_drug(target_id, top_k)

class BatchPredictionRequest(BaseModel):
    compound_ids: List[int]
    top_k: int = 10

@router.post("/batch", summary="Predict for multiple drugs")
def predict_batch(request: BatchPredictionRequest):
    """
    Batch prediction for a list of compound IDs.
    Matches the 'predict_for_compounds' example from the R-GCN usage.
    """
    results = []
    for cid in request.compound_ids:
        try:
            # Re-use existing logic, but handle errors gracefully for batch
            if scores is not None and cid < len(scores):
                pred = predict_drug(cid, request.top_k)
                results.append(pred)
            else:
                results.append({"compound_id": cid, "error": "Invalid ID or Matrix not loaded"})
        except HTTPException as e:
             results.append({"compound_id": cid, "error": e.detail})
             
    return {"batch_predictions": results}

