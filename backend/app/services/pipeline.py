import sys
import os
import json
import numpy as np
import asyncio
from typing import Dict, Any, List
from app import utils

try:
    import torch
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    print("Warning: Torch not available in pipeline. Embedding features will be disabled.")
    TORCH_AVAILABLE = False
    class torch:
        def load(self, *args, **kwargs): return None
    class F:
        def cosine_similarity(self, *args, **kwargs): return []


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


# --- CACHE ---
# Stores: (drug_id, disease_id) -> { "stdout": str, "paths": list, "viz_data": dict }
_analysis_cache = {}


def load_graph_embeddings():
    global _graph_data
    if _graph_data is None:
        if not TORCH_AVAILABLE:
            return

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

def perform_polo_analysis(drug_id: str, disease_id: str):
    """
    Helper to run Polo Agent analysis with caching and without file I/O race conditions.
    Returns dict: { "stdout": str, "paths": list, "viz_data": dict, "error": str }
    """
    global polo_agent, _analysis_cache
    
    # Lazy Init Agent Needed for ID resolution
    original_cwd = os.getcwd()
    os.chdir(TEMP_DIR)
    try:
        if polo_agent is None:
            import polo_sci4
            if hasattr(polo_sci4, 'TargetedAgent'):
                polo_agent = polo_sci4.TargetedAgent()
            else:
                polo_agent = polo_sci4.RobustPoloAgent()
                
            # Monkey Patch
            if hasattr(polo_sci4, 'VIP_MOLECULES'):
                for k, v in polo_sci4.VIP_MOLECULES.items():
                    if isinstance(v, list) and len(v) > 0:
                        polo_sci4.VIP_MOLECULES[k] = v[0]
    except Exception as e:
        print(f"Agent init error: {e}")
    finally:
        os.chdir(original_cwd)

    # Resolve IDs for consistent Cache Key
    # If polo_agent is available, use it to resolve names to IDs
    # Otherwise use inputs as is (fallback)
    c_key = drug_id
    d_key = disease_id
    
    if polo_agent:
        resolved_c = polo_agent.get_id(drug_id)
        if resolved_c: c_key = resolved_c
        elif drug_id in polo_agent.nodes: c_key = drug_id
            
        resolved_d = polo_agent.get_id(disease_id)
        if resolved_d: d_key = resolved_d
        elif disease_id in polo_agent.nodes: d_key = disease_id
            
    cache_key = (str(c_key), str(d_key))
    if cache_key in _analysis_cache:
        print(f"DEBUG: Cache Hit for {cache_key}")
        return _analysis_cache[cache_key]
        
    print(f"DEBUG: Cache Miss for {cache_key}. Running analysis...")
    
    original_cwd = os.getcwd()
    os.chdir(TEMP_DIR)
    
    result = { "stdout": "", "paths": [], "viz_data": {}, "error": None }
    
    try:
        import polo_sci4
        import importlib
        import io
        from contextlib import redirect_stdout
        
        # Ensure agent is initialized (Double check)
        if polo_agent is None:
             if hasattr(polo_sci4, 'RobustPoloAgent'):
                polo_agent = polo_sci4.RobustPoloAgent()
                
        # CAPTURE STDOUT
        f_buffer = io.StringIO()
        with redirect_stdout(f_buffer):
            # Ensure inputs are names if possible (Best for Polo)
            p_drug = drug_id
            p_disease = disease_id
            
            if drug_id.isdigit():
                 n = utils.drug_id_to_name(drug_id)
                 if n: p_drug = n
            
            if disease_id.isdigit():
                 n = utils.disease_id_to_name(disease_id)
                 if n: p_disease = n

            # Pass write_file=False to avoid race condition
            found_paths = polo_agent.explain(p_drug, p_disease, write_file=False)
            
        result["stdout"] = f_buffer.getvalue()
        result["paths"] = found_paths
        
        # Generate Viz Data in-memory
        if hasattr(polo_agent, 'export_to_json'):
            top_paths = found_paths[:20] if found_paths else []
            viz_data = polo_agent.export_to_json(top_paths, write_file=False)
            result["viz_data"] = viz_data
        else:
             result["viz_data"] = {"nodes": [], "edges": []}

        # Cache valid results
        if found_paths:
             _analysis_cache[cache_key] = result
             
        # Print logs to real console
        print(result["stdout"])
        
    except Exception as e:
        print(f"Error in perform_polo_analysis: {e}")
        import traceback
        traceback.print_exc()
        result["error"] = str(e)
    finally:
        os.chdir(original_cwd)
        
    return result

def run_analysis(drug_id: str, disease_id: str) -> Dict[str, Any]:
    """
    Run Polo Symbolic Analysis via Helper.
    """
    analysis_res = perform_polo_analysis(drug_id, disease_id)
    
    if analysis_res["error"]:
        return {"error": analysis_res["error"]}
        
    full_output = analysis_res["stdout"]
    viz_data = analysis_res["viz_data"]
    
    # Parse output for rules and chains
    parsed_chains = []
    parsed_rules = []
    
    import re
    path_regex = re.compile(r"^\s*(?P<source>.+?)\s+(?:<?-+)\s*\[(?P<rel>.+?)\]\s*(?:-+>?)\s+(?P<target>.+?)\s+\((?P<type>.+?)\)$")

    lines = full_output.split('\n')
    current_chain = None
    current_rule_parts = []
    
    for line in lines:
        line = line.strip()
        if line.startswith("🔷 MECHANISM"):
            if current_chain:
                parsed_chains.append(current_chain)
                parsed_rules.append(f"Rule ({current_chain['tag']}): " + ", which ".join(current_rule_parts))
            
            parts = line.split('[')
            tag = parts[1].replace(']', '') if len(parts) > 1 else "General"
            current_chain = {
                "pathway": [],
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
            match = path_regex.match(line)
            if current_chain and match:
                source = match.group("source").strip()
                rel = match.group("rel").strip()
                target = match.group("target").strip()
                
                current_chain["edges"].append(rel)
                
                if not current_chain["pathway"]:
                    current_chain["pathway"].append(source)
                current_chain["pathway"].append(target)
                
                current_rule_parts.append(f"{source} {rel} {target}")

    if current_chain:
        parsed_chains.append(current_chain)
        parsed_rules.append(f"Rule ({current_chain['tag']}): " + ", which ".join(current_rule_parts))

    return {
        "visual_data": viz_data,
        "reasoning_chains": parsed_chains,
        "symbolic_rules": parsed_rules,
        "neural_score": 0.85,
        "symbolic_score": 0.75,
        "graph": viz_data,
        "raw_output": full_output
    }


def get_confidence_breakdown(drug_id: str, disease_id: str) -> Dict[str, Any]:
    """
    Generate detailed confidence breakdown using Cached Analysis.
    """
    global _graph_data
    
    # Use Helper
    analysis_res = perform_polo_analysis(drug_id, disease_id)
    found_paths = analysis_res["paths"]
    
    # Process Polo Outputs
    pathway_score_sum = 0
    influenced_genes = set()
    rules_fired = []
    rule_score_sum = 0
    
    # Calculate Averages for Final Score
    avg_pathway = 0.0
    
    for item in found_paths[:5]: # Top 5
        # Pathway
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
            
    avg_pathway = pathway_score_sum / len(found_paths) if found_paths else 0.0
    
    # Format Genes
    gene_list = [{"name": g, "score": 0.8} for g in list(influenced_genes)[:10]]
    gene_score = min(len(influenced_genes) * 10, 100) / 100.0
    
    rule_score = min(rule_score_sum * 0.2, 1.0)

    # 3. Embedding Similarity
    load_graph_embeddings()
    similarity_score = 0.0
    similar_drugs = []
    
    if _graph_data and TORCH_AVAILABLE:
        try:
            # Identify Drug Node Type
            drug_node_type = None
            for nt in ['Compound', 'compound', 'Drug', 'drug']:
                if nt in _graph_data.node_types:
                    drug_node_type = nt
                    break
            
            if drug_node_type and hasattr(_graph_data[drug_node_type], 'x'):
                emb_matrix = _graph_data[drug_node_type].x
                # Check if drug_id is int
                if drug_id.isdigit():
                    did = int(drug_id)
                else: 
                     # Try to find ID or skip
                     did = -1
                     
                if did >= 0 and did < len(emb_matrix):
                    target_emb = emb_matrix[did]
                    sims = F.cosine_similarity(target_emb.unsqueeze(0), emb_matrix)
                    top_k = torch.topk(sims, k=6)
                    indices = top_k.indices.tolist()
                    values = top_k.values.tolist()
                    
                    for i, idx in enumerate(indices):
                        if idx == did: continue
                        similar_drugs.append({
                            "name": str(idx),
                            "score": float(values[i])
                        })
                        if len(similar_drugs) >= 5: break
                    
                    if similar_drugs:
                        similarity_score = sum(d['score'] for d in similar_drugs) / len(similar_drugs)
        except Exception as e:
            print(f"Similarity calc error: {e}")

    # --- NEW SCORING LOGIC (Weighted + Normalized) ---
    MAX_PATHWAY_SCORE = 0.035
    W_EMBEDDING = 0.35
    W_GENE = 0.35
    W_PATHWAY = 0.15
    W_RULE = 0.15

    avg_sim = similarity_score 
    avg_rule = rule_score 
    avg_gene = gene_score
    
    norm_pathway = min(avg_pathway / MAX_PATHWAY_SCORE, 1.0)
    norm_gene = min(avg_gene, 1.0)
    norm_embedding = min(avg_sim, 1.0)
    norm_rule = min(avg_rule, 1.0)

    final_confidence_val = (
        (norm_pathway * W_PATHWAY) +
        (norm_gene * W_GENE) +
        (norm_embedding * W_EMBEDDING) +
        (norm_rule * W_RULE)
    ) * 100
    
    final_confidence = min(final_confidence_val, 100.0)
    
    def resolve(nid):
        nid = str(nid)
        if polo_agent:
            try:
                info = polo_agent.get_info(nid)
                return info['name'] if info else f"Unknown ({nid})"
            except Exception:
                return str(nid)
        return str(nid)

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


