import sys
import os
import json
import numpy as np
import asyncio
from typing import Dict, Any, List
import torch
import torch.nn.functional as F


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
_graph_data = None
# Adjust path to find finalKG
# from backend/app/services -> ../../../finalKG
KG_GRAPH_PATH = os.path.join(PROJECT_ROOT, "../finalKG/data/graph_with_embeddings.pt")
if not os.path.exists(KG_GRAPH_PATH):
    KG_GRAPH_PATH = os.path.join(PROJECT_ROOT, "../data/graph.pt")
# If still failing, try absolute path based on user environment
if not os.path.exists(KG_GRAPH_PATH):
    # Try hardcoded
    KG_GRAPH_PATH = r"c:\Users\kabhi\neurosymbolic\finalKG\data\graph.pt"


def load_graph_embeddings():
    global _graph_data
    if _graph_data is None:
        if os.path.exists(KG_GRAPH_PATH):
            print(f"Loading Graph Embeddings from {KG_GRAPH_PATH}...")
            # weights_only=False required for PyG HeteroData
            try:
                _graph_data = torch.load(KG_GRAPH_PATH, weights_only=False)
                print("Graph Embeddings loaded.")
            except Exception as e:
                print(f"Error loading graph embeddings: {e}")
        else:
            print(f"Error: {KG_GRAPH_PATH} not found.")


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
        
        if polo_agent is None:
            if hasattr(polo_sci4, 'TargetedAgent'):
                polo_agent = polo_sci4.TargetedAgent()
            else:
                polo_agent = polo_sci4.RobustPoloAgent()
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

def get_confidence_breakdown(drug_id: str, disease_id: str) -> Dict[str, Any]:
    """
    Generate detailed confidence breakdown.
    1. Pathway Match (via Polo)
    2. Gene Influence (via Polo paths)
    3. Embedding Similarity (via graph.pt)
    4. Rule Reasoning (via Polo tags)
    """
    global polo_agent, _graph_data
    
    # 1. & 2. & 4. Run Polo to get paths and rules
    # We need to run explain and capture the RETURNED paths (not just json)
    # Ensure polo is initialized
    original_cwd = os.getcwd()
    os.chdir(TEMP_DIR)
    found_paths = []
    
    try:
        import polo_sci4
        if polo_agent is None:
            # Check which class exists
            if hasattr(polo_sci4, 'TargetedAgent'):
                polo_agent = polo_sci4.TargetedAgent()
            elif hasattr(polo_sci4, 'RobustPoloAgent'):
                polo_agent = polo_sci4.RobustPoloAgent()
            else:
                 print("Error: neither TargetedAgent nor RobustPoloAgent found in polo_sci4")
                 return []
        
        # Capture the returned paths
        found_paths = polo_agent.explain(drug_id, disease_id)
        if not found_paths:
            found_paths = []

            
    except Exception as e:
        print(f"Error in Polo for confidence: {e}")
        # Fallback to empty if fails
        found_paths = []
    finally:
        os.chdir(original_cwd)

    # Process Polo Outputs
    # Pathway Match
    # Extract top pathways (formatted as string representations)
    pathway_list = []
    pathway_score_sum = 0
    
    # Gene Influence
    influenced_genes = set()
    
    # Rule Reasoning
    rules_fired = []
    rule_score_sum = 0
    
    # Calculate Averages for Final Score
    avg_pathway = pathway_score_sum / len(found_paths) if found_paths else 0.0
    # Iterate to populate lists
    for item in found_paths[:5]: # Top 5
        # Pathway
        p_str = " -> ".join(item.get('path', [])) # Simplified
        pathway_list.append({"path": p_str, "score": item.get('score', 0)})
        pathway_score_sum += item.get('score', 0)
        
        # Genes (simple heuristic: any node not drug/disease/chem/anat)
        for node in item.get('path', []):
            influenced_genes.add(node)
            
        # Rules
        tag = item.get('tag', 'General')
        if tag not in [r['name'] for r in rules_fired]:
            rules_fired.append({"name": tag, "explanation": "Logic rule triggered", "strength": "High" if "VIA" in tag else "Medium"})
            if "VIA" in tag: rule_score_sum += 1.0
            else: rule_score_sum += 0.5
            
    # Format Genes
    gene_list = [{"name": g, "score": 0.8} for g in list(influenced_genes)[:10]] # Limit to 10
    gene_score = min(len(influenced_genes) * 10, 100) / 100.0 # Normalized
    
    rule_score = min(rule_score_sum * 0.2, 1.0) # Heuristic

    # 3. Embedding Similarity
    load_graph_embeddings()
    similarity_score = 0.0
    similar_drugs = []
    
    if _graph_data:
        try:
            # Identify Drug Node Type
            # Try 'Compound' first (Hetionet standard), then others
            drug_node_type = None
            for nt in ['Compound', 'compound', 'Drug', 'drug']:
                if nt in _graph_data.node_types:
                    drug_node_type = nt
                    break
            
            if drug_node_type and hasattr(_graph_data[drug_node_type], 'x'):
                emb_matrix = _graph_data[drug_node_type].x
                did = int(drug_id)
                if did < len(emb_matrix):
                    target_emb = emb_matrix[did]
                    
                    # Compute Cosine Similarity with ALL drugs
                    sims = F.cosine_similarity(target_emb.unsqueeze(0), emb_matrix)
                    
                    # Get top k (exclude self)
                    top_k = torch.topk(sims, k=6) # Top 6 (self + 5)
                    
                    indices = top_k.indices.tolist()
                    values = top_k.values.tolist()
                    
                    for i, idx in enumerate(indices):
                        if idx == did: continue
                        similar_drugs.append({
                            "name": str(idx), # Resolve name if possible
                            "score": float(values[i])
                        })
                        if len(similar_drugs) >= 5: break
                    
                    # Avg similarity of top 5
                    if similar_drugs:
                        similarity_score = sum(d['score'] for d in similar_drugs) / len(similar_drugs)
        except Exception as e:
            print(f"Similarity calc error: {e}")

    # --- NEW SCORING LOGIC (Weighted + Normalized) ---
    MAX_PATHWAY_SCORE = 0.0056
    
    W_PATHWAY = 0.05
    W_GENE = 0.60
    W_EMBEDDING = 0.30
    W_RULE = 0.05

    # Calculate raw averages
    avg_pathway = pathway_score_sum / len(found_paths) if found_paths else 0.0
    avg_gene = gene_score 
    avg_sim = similarity_score 
    avg_rule = rule_score 
    
    # Normalize
    # Pathway: scaled by max observed score
    norm_pathway = min(avg_pathway / MAX_PATHWAY_SCORE, 1.0)
    
    # Gene/Sim/Rule are already ~0-1 (or we can clamp them)
    norm_gene = min(avg_gene, 1.0)
    norm_embedding = min(avg_sim, 1.0)
    norm_rule = min(avg_rule, 1.0)

    # Final Formula
    final_confidence_val = (
        (norm_pathway * W_PATHWAY) +
        (norm_gene * W_GENE) +
        (norm_embedding * W_EMBEDDING) +
        (norm_rule * W_RULE)
    ) * 100
    
    final_confidence = min(final_confidence_val, 100.0)
    
    # Resolve Names for Details
    # (Helper function unchanged)
    def resolve(nid):
        nid = str(nid) # Safety cast for integer IDs
        if polo_agent:
            try:
                info = polo_agent.get_info(nid)
                return info['name'] if info else f"Unknown ({nid})"
            except Exception:
                return str(nid)
        return str(nid)

    # Re-construct detailed lists with names
    detailed_pathways = []
    for item in found_paths[:5]:
        named_path = []
        for pid in item.get('path', []):
            named_path.append(resolve(pid))
        detailed_pathways.append({"path": " -> ".join(named_path), "score": item.get('score', 0)})
        
    detailed_genes = []
    for g in gene_list:
        detailed_genes.append({"name": resolve(g['name']), "score": g['score']})
        
    detailed_sim_drugs = []
    for d in similar_drugs:
        detailed_sim_drugs.append({"name": resolve(d['name']), "score": d['score']})
        
    return {
      "averages": {
        "pathway": round(avg_pathway, 6),
        "gene_influence": round(avg_gene, 4),
        "embedding_similarity": round(avg_sim, 4),
        "rule_mining": round(avg_rule, 4),
        "final_confidence": round(final_confidence, 2)
      },
      "normalized": {
        "pathway": round(norm_pathway, 4),
        "gene_influence": round(norm_gene, 4),
        "embedding_similarity": round(norm_embedding, 4),
        "rule_mining": round(norm_rule, 4)
      },
      "details": {
        "pathways": detailed_pathways,
        "gene_influence": detailed_genes,
        "similar_drugs": detailed_sim_drugs,
        "rules": rules_fired
      }
    }


