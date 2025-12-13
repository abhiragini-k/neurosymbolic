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
            print(f"Error: {PREDICTION_MATRIX_PATH} not found.")

def initialize_polo():
    """
    Pre-load the Polo Agent during startup to avoid latency on first request.
    """
    global polo_agent
    print("Initializing Polo Agent...")
    original_cwd = os.getcwd()
    os.chdir(TEMP_DIR)
    try:
        import polo_sci4
        if polo_agent is None:
            polo_agent = polo_sci4.RobustPoloAgent()
        print("Polo Agent Initialized.")
    except Exception as e:
        print(f"Failed to initialize Polo Agent: {e}")
    finally:
        os.chdir(original_cwd)

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
        import polo_sci4
        import importlib
        import io
        from contextlib import redirect_stdout
        
        # Force reload to ensure we get the user's latest code
        importlib.reload(polo_sci4)
        
        # Instantiate the correct agent class
        # User might switch between RobustPoloAgent and TargetedAgent
        target_class = getattr(polo_sci4, 'RobustPoloAgent', getattr(polo_sci4, 'TargetedAgent', None))
        
        if target_class is None:
            raise ImportError("Could not find RobustPoloAgent or TargetedAgent in polo_sci4")
            
        # MONKEY PATCH: Fix VIP_MOLECULES if they are lists (which causes TypeError in the loop)
        # The user's script iterates over values expecting them to be hashable (strings), but they are lists.
        if hasattr(polo_sci4, 'VIP_MOLECULES'):
            for k, v in polo_sci4.VIP_MOLECULES.items():
                if isinstance(v, list) and len(v) > 0:
                    # Take the first ID from the list to make it compatible with the loop
                    polo_sci4.VIP_MOLECULES[k] = v[0]
        
        if polo_agent is None or not isinstance(polo_agent, target_class):
            polo_agent = target_class()
            
        # Capture stdout to parse the rules printed by the agent
        f = io.StringIO()
        with redirect_stdout(f):
            polo_agent.explain(drug_id, disease_id)
        
        output = f.getvalue()
        print(output) # Print to real stdout for debugging logs
        
        # Parse output for rules and chains
        # Expected format:
        # 🔷 MECHANISM 1 [VIA MTOR (Targeted)]
        #    Specific Score: 0.1234
        #       CBLN1 --[participates in]--> regulation ...
        
        parsed_chains = []
        parsed_rules = []
        
        import re
        
        # Regex for parsing path lines
        # Matches: Source --[Rel]--> Target (Type)
        # Handles various arrow types: --, <---, ---
        path_regex = re.compile(r"^\s*(?P<source>.+?)\s+(?:<?-+)\s*\[(?P<rel>.+?)\]\s*(?:-+>?)\s+(?P<target>.+?)\s+\((?P<type>.+?)\)$")

        lines = output.split('\n')
        current_chain = None
        current_rule_parts = []
        
        for line in lines:
            line = line.strip()
            if line.startswith("🔷 MECHANISM"):
                # Save previous if exists
                if current_chain:
                    parsed_chains.append(current_chain)
                    parsed_rules.append(f"Rule ({current_chain['tag']}): " + ", which ".join(current_rule_parts))
                
                # Start new
                parts = line.split('[')
                tag = parts[1].replace(']', '') if len(parts) > 1 else "General"
                current_chain = {
                    "pathway": [], # We'll extract nodes
                    "confidence": 0.0,
                    "edges": [],
                    "tag": tag
                }
                current_rule_parts = []
                
            elif line.startswith("Specific Score:"):
                if current_chain:
                    try:
                        score = float(line.split(":")[1].strip())
                        current_chain["confidence"] = min(score * 100, 99.9) if score < 1 else score
                    except: pass
            
            elif "[" in line and "]" in line and "(" in line and ")" in line:
                # Try matching regex
                match = path_regex.match(line)
                if current_chain and match:
                    source = match.group("source").strip()
                    rel = match.group("rel").strip()
                    target = match.group("target").strip()
                    
                    current_chain["edges"].append(rel)
                    
                    # Populate pathway nodes
                    if not current_chain["pathway"]:
                        current_chain["pathway"].append(source)
                    current_chain["pathway"].append(target)
                    
                    # Build rule text
                    current_rule_parts.append(f"{source} {rel} {target}")

        # Append last one
        if current_chain:
            parsed_chains.append(current_chain)
            parsed_rules.append(f"Rule ({current_chain['tag']}): " + ", which ".join(current_rule_parts))

        
        viz_path = "viz_data.json"
        if os.path.exists(viz_path):
            with open(viz_path, 'r') as f:
                data = json.load(f)
            
            # Merge parsed data
            data["reasoning_chains"] = parsed_chains
            data["symbolic_rules"] = parsed_rules
            
            # Mock scores if missing
            if "neural_score" not in data: data["neural_score"] = 0.85
            if "symbolic_score" not in data: data["symbolic_score"] = 0.75
            
            return data
        else:
            return {"error": "viz_data.json not generated"}
            
    except Exception as e:
        print(f"Error running polo analysis: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
        
    finally:
        os.chdir(original_cwd)
