import numpy as np
from fastapi import FastAPI
import json
import os
import sys
import io
from contextlib import redirect_stdout
from pydantic import BaseModel

app = FastAPI()

print("--------------------------------------------------")
print("   🚀 STARTING BACKEND V2 (API/ANALYSIS FIX) 🚀   ")
print("--------------------------------------------------")

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Navigate up to neurosymbolic, then down to R-GCN-MODEL
MODEL_DIR = os.path.join(os.path.dirname(BASE_DIR), "R-GCN-MODEL")
PREDICTION_MATRIX_PATH = os.path.join(MODEL_DIR, "compound_disease_predictions.npy")

# --- POLO AGENT SETUP ---
TEMP_DIR = os.path.join(os.path.dirname(BASE_DIR), "temp")
sys.path.append(TEMP_DIR)

polo_agent = None
name_to_polo_id = {}

def init_polo_agent():
    global polo_agent
    print("Initializing Polo Agent...")
    try:
        cwd = os.getcwd()
        os.chdir(TEMP_DIR)
        from polo_sci4 import RobustPoloAgent
        polo_agent = RobustPoloAgent()
        
        os.chdir(cwd)
        print("Polo Agent initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Polo Agent: {e}")
        os.chdir(cwd)

# Initialize on startup (or immediately)
init_polo_agent()

# Load the prediction matrix once
print(f"Loading prediction matrix from {PREDICTION_MATRIX_PATH}...")
try:
    scores = np.load(PREDICTION_MATRIX_PATH, allow_pickle=True).astype(float)
    print(f"Matrix loaded. Shape: {scores.shape}")
except FileNotFoundError:
    print(f"Error: {PREDICTION_MATRIX_PATH} not found!")
    scores = np.zeros((1, 1)) # Fallback

# Load mappings (optional)
compound_names = {}
disease_names = {}

def load_mappings():
    global compound_names, disease_names
    print("Loading mappings...")
    try:
        compound_names = json.load(open(os.path.join(BASE_DIR, "compound_id_to_name.json")))
        disease_names = json.load(open(os.path.join(BASE_DIR, "disease_id_to_name.json")))
        print(f"Mappings loaded. Compounds: {len(compound_names)}, Diseases: {len(disease_names)}")
    except Exception as e:
        print(f"Warning: JSON mappings not found or error: {e}")
        compound_names = {}
        disease_names = {}

load_mappings()

# 1️⃣ API — Predict top diseases for a compound
@app.get("/predict/drug/{compound_id}")
def predict_drug(compound_id: int, top_k: int = 10):
    if not compound_names: load_mappings()
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
    if not compound_names: load_mappings()
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

class DrugRequest(BaseModel):
    drug_name: str

# 3️⃣ API — Predict by drug name (POST)
@app.post("/predict/drug")
def predict_drug_post(request: DrugRequest):
    if not compound_names: load_mappings()
    drug_name = request.drug_name
    # Invert mapping to find ID
    target_id = None
    for cid, name in compound_names.items():
        if name.lower() == drug_name.lower():
            target_id = int(cid)
            break
            
    if target_id is None:
        return {"error": f"Drug '{drug_name}' not found in mapping"}
        
    # Get predictions using existing logic
    if target_id >= len(scores):
        return {"error": f"Compound ID {target_id} out of range"}
        
    compound_scores = scores[target_id]
    top_k = 10
    top_indices = compound_scores.argsort()[-top_k:][::-1]

    results = []
    for rank, disease_id in enumerate(top_indices, 1):
        results.append({
            "compound_id": target_id,
            "compound_name": compound_names.get(str(target_id), str(target_id)),
            "disease_id": int(disease_id),
            "disease_name": disease_names.get(str(disease_id), str(disease_id)),
            "score": float(compound_scores[disease_id]),
        })
    
    # Return in format expected by frontend
    return {
        "drug_id": target_id,
        "predicted": results
    }

# 3b API — Predict by drug name (GET - Legacy/Bonus)
@app.get("/predict/drug-name/{drug_name}")
def predict_drug_by_name(drug_name: str, top_k: int = 10):
    if not compound_names: load_mappings()
    # Invert mapping to find ID
    target_id = None
    for cid, name in compound_names.items():
        if name.lower() == drug_name.lower():
            target_id = int(cid)
            break
            
    if target_id is None:
        return {"error": f"Drug '{drug_name}' not found in mapping"}
        
    return predict_drug(target_id, top_k)

# 4️⃣ API — Neurosymbolic Analysis
# RENAMED to /api/analysis to avoid collision with frontend route /analysis/detail
@app.get("/api/analysis/{compound_id}/{disease_id}")
def analyze_connection(compound_id: int, disease_id: int, drug_name: str = None, disease_name: str = None):
    if not compound_names: load_mappings()
    
    # 1. Get Names
    # Use provided names if available, otherwise fallback to mapping
    c_name = drug_name if drug_name else compound_names.get(str(compound_id), str(compound_id))
    d_name = disease_name if disease_name else disease_names.get(str(disease_id), str(disease_id))
    
    # CRITICAL: If name is still an ID (digits), try to resolve it from mapping
    if str(c_name).isdigit() and str(c_name) in compound_names:
        c_name = compound_names[str(c_name)]
    if str(d_name).isdigit() and str(d_name) in disease_names:
        d_name = disease_names[str(d_name)]
    
    print(f"DEBUG: analyze_connection called with {compound_id}, {disease_id}")
    print(f"DEBUG: Received params - drug_name: '{drug_name}', disease_name: '{disease_name}'")
    print(f"DEBUG: Resolved names: '{c_name}', '{d_name}'")

    # 2. Get Scores
    neural_score = 0.0
    if compound_id < scores.shape[0] and disease_id < scores.shape[1]:
        neural_score = float(scores[compound_id, disease_id])
        
    # 3. Run Symbolic Analysis
    if not polo_agent:
        return {"error": "Polo Agent not active", "neural_score": neural_score}
        
    # Capture Output
    output_buffer = io.StringIO()
    viz_data = {"nodes": [], "edges": []}
    
    try:
        cwd = os.getcwd()
        os.chdir(TEMP_DIR) # Switch to temp for file output
        
        print(f"DEBUG: Calling polo_agent.explain('{c_name}', '{d_name}')")
        
        with redirect_stdout(output_buffer):
            # Pass NAMES directly as per updated polo_sci4.py
            polo_agent.explain(c_name, d_name)
            
        # Read generated JSON
        if os.path.exists("viz_data.json"):
            with open("viz_data.json", "r") as f:
                viz_data = json.load(f)
                
        os.chdir(cwd)
    except Exception as e:
        os.chdir(cwd)
        return {"error": str(e), "neural_score": neural_score}
        
    # Parse text output for rules/chains
    full_output = output_buffer.getvalue()
    
    # Check for error messages in output
    if "Error:" in full_output and "not found in database" in full_output:
         return {
            "error": f"Polo Analysis Failed: {full_output.strip()}",
            "neural_score": neural_score,
            "symbolic_rules": [],
            "graph": {"nodes": [], "edges": []},
            "raw_output": full_output
        }

    lines = full_output.split('\n')
    symbolic_rules = []
    reasoning_chains = []
    
    current_chain_obj = {"pathway": [], "edges": [], "confidence": 0.0}
    current_nodes = []
    
    import re
    score_pattern = re.compile(r"Specific Score: ([\d.]+)")
    # Split by arrow pattern: Node1 --[relation]--> Node2 (Type)
    arrow_pattern = re.compile(r"\s+(?:--\[|---\[|<---\[)(.+?)(?:\]-->|\]---|\]---)\s+")

    for line in lines:
        clean = line.strip()
        if not clean: continue
        
        if clean.startswith("🔷 MECHANISM"):
            if current_nodes:
                current_chain_obj["pathway"] = current_nodes
                reasoning_chains.append(current_chain_obj)
            
            current_chain_obj = {"pathway": [], "edges": [], "confidence": 0.0}
            current_nodes = []
            symbolic_rules.append(clean)
            
        elif "Specific Score:" in clean:
            match = score_pattern.search(clean)
            if match:
                try:
                    current_chain_obj["confidence"] = float(match.group(1))
                except: pass
            symbolic_rules.append(clean)
            
        elif "-->" in clean or "<--" in clean or "---" in clean:
            # Add to symbolic rules
            symbolic_rules.append(clean)
            
            # Parse edge
            parts = arrow_pattern.split(clean)
            # parts: [Node1, Relation, Node2 (Type)]
            if len(parts) >= 3:
                u_n = parts[0].strip()
                rel = parts[1].strip()
                rest = parts[2].strip()
                # rest is "Node2 (Type)"
                # Remove type info: "Node2 (Type)" -> "Node2"
                if " (" in rest and rest.endswith(")"):
                    v_n = rest.rsplit(" (", 1)[0]
                else:
                    v_n = rest
                
                if not current_nodes:
                    current_nodes.append(u_n)
                current_nodes.append(v_n)
                current_chain_obj["edges"].append(rel)
            
    if current_nodes:
        current_chain_obj["pathway"] = current_nodes
        reasoning_chains.append(current_chain_obj)

    return {
        "compound_name": c_name,
        "disease_name": d_name,
        "neural_score": neural_score,
        "symbolic_score": 0.95, # Placeholder
        "symbolic_rules": symbolic_rules,
        "reasoning_chains": reasoning_chains,
        "graph": viz_data,
        "raw_output": full_output
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
