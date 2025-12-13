from explainability.gnn_service import gnn_service
import random

def compute_gene_match(drug_id: str, disease_id: str):
    """
    Computes per-gene drug vs disease activation match using GNN importance for gene selection.
    """
    
    # Seed random number generator for reproducibility
    seed_str = f"{drug_id}_{disease_id}_gene_match"
    random.seed(int(hash(seed_str) % 10**8))

    # 1. Get Top Genes from GNN
    gene_importance_map = gnn_service.get_gene_importance(drug_id, disease_id)
    
    if not gene_importance_map:
        # Fallback if no model/map
        target_genes = ["AMPK", "MTOR", "FOXO1", "NFKB1", "TP53", "AKT1", "TNF", "IL6", "BCL2", "MYC"]
    else:
        # Sort by score descending and take top 20
        sorted_genes = sorted(gene_importance_map.items(), key=lambda x: x[1], reverse=True)
        target_genes = [g[0] for g in sorted_genes[:20]]
    
    matches = []
    
    for gene in target_genes:
        # Mock drug effect: 1 (up), -1 (down), 0 (neutral)
        # Weighted slightly towards non-neutral for interest
        drug_effect = random.choices([1, -1, 0], weights=[0.4, 0.4, 0.2])[0]
        
        # Mock disease signature: 1 (up), -1 (down), 0 (neutral)
        disease_sig = random.choices([1, -1, 0], weights=[0.4, 0.4, 0.2])[0]
        
        # TEMP MOCK RULE:
        # If both drug and disease effect are the same -> score = random(0.7-1.0)
        # If opposite -> score = random(0.0-0.3)
        if drug_effect == disease_sig and drug_effect != 0:
             # Same direction (both up or both down) -> Good Match
             score = random.uniform(0.7, 1.0)
        elif drug_effect == -disease_sig and drug_effect != 0:
             # Opposite direction -> Conflict
             score = random.uniform(0.0, 0.3)
        else:
             # Mixed/Neutral -> Partial
             score = random.uniform(0.3, 0.7)
             
        matches.append({
            "gene": gene,
            "drug": drug_effect,
            "disease": disease_sig,
            "match": round(score, 2)
        })
        
    return {"gene_matches": matches}
