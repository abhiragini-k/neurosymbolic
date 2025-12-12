import sys
import os
import json
import numpy as np
import asyncio
from typing import Dict, Any, List

# --- Path Configuration ---
# Current file: backend/app/services/pipeline.py
# Backend Root: backend/
# Project Root: neurosymbolic/ (contains temp/ and R-GCN-MODEL/)

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
TEMP_DIR = os.path.join(PROJECT_ROOT, "temp")
RGCN_MODEL_DIR = os.path.join(PROJECT_ROOT, "R-GCN-MODEL")
PREDICTION_MATRIX_PATH = os.path.join(RGCN_MODEL_DIR, "compound_disease_predictions.npy")

# Ensure temp is in path for polo_sci4 import
if TEMP_DIR not in sys.path:
    sys.path.append(TEMP_DIR)

# Lazy import handle
polo_agent = None

# Cache for R-GCN scores
_rgcn_scores = None

def load_rgcn_matrix():
    global _rgcn_scores
    if _rgcn_scores is None:
        if os.path.exists(PREDICTION_MATRIX_PATH):
            print(f"Loading R-GCN Matrix from {PREDICTION_MATRIX_PATH}...")
            _rgcn_scores = np.load(PREDICTION_MATRIX_PATH, allow_pickle=True).astype(float)
            print("R-GCN Matrix loaded.")
        else:
            print(f"Error: {PREDICTION_MATRIX_PATH} not found.")

def run_rgcn(drug_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Run R-GCN model prediction for a drug.
    Returns list of {disease_id: ..., score: ...}
    """
    load_rgcn_matrix()
    
    if _rgcn_scores is None:
        raise ValueError("R-GCN model not loaded")
    
    try:
        cid = int(drug_id)
    except ValueError:
        raise ValueError(f"Invalid drug_id: {drug_id}")
        
    if cid >= len(_rgcn_scores):
        return [] # ID out of range
        
    compound_scores = _rgcn_scores[cid]
    # Get top K indices
    top_indices = compound_scores.argsort()[-top_k:][::-1]
    
    results = []
    for disease_id in top_indices:
        results.append({
            "disease_id": str(disease_id),
            "score": float(compound_scores[disease_id])
        })
        
    return results

def run_analysis(drug_id: str, disease_id: str) -> Dict[str, Any]:
    """
    Run Polo Symbolic Analysis.
    This calls polo_sci4.py and saves output to temp/viz_data.json.
    """
    global polo_agent
    
    # Change working directory to temp so polo_sci4 can find its local files (nodes.csv, etc.)
    original_cwd = os.getcwd()
    os.chdir(TEMP_DIR)
    
    try:
        # Import polo_sci4 only when needed and in correct dir
        # Re-import if needed to ensure fresh state or just instantiate once
        # The script has `if __name__ == "__main__":` so import is safe
        import polo_sci4
        
        if polo_agent is None:
            polo_agent = polo_sci4.TargetedAgent()
            
        # The agent.explain method prints to stdout and saves to viz_data.json
        # We need to capture the fact it ran.
        # It currently does not return the data, but saves it to file.
        # We will read that file to return it to API caller if needed, 
        # or just confirm it saved. 
        # Requirement: "Return same output back to frontend as API response"
        
        # We need to suppress stdout or just let it print
        print(f"Running Polo Analysis: {drug_id} -> {disease_id}")
        
        # NOTE: polo_sci4.explain calls export_to_json("viz_data.json")
        # generated path will be in TEMP_DIR because we chdir'd there
        polo_agent.explain(drug_id, disease_id)
        
        viz_path = "viz_data.json"
        if os.path.exists(viz_path):
            with open(viz_path, 'r') as f:
                data = json.load(f)
            return data
        else:
            return {"error": "viz_data.json not generated"}
            
    except Exception as e:
        print(f"Error running polo analysis: {e}")
        return {"error": str(e)}
        
    finally:
        os.chdir(original_cwd)
