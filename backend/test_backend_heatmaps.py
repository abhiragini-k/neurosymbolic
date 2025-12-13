import sys
import os
import json

# Add backend directory to sys.path
sys.path.append(os.path.abspath("d:/codered/neurosymbolic/backend"))

from explainability.pathway_influence import compute_pathway_influence
from explainability.gene_match import compute_gene_match

def test_heatmaps():
    # Use valid IDs from mapping
    drug_id = "1" # Bromhexine
    disease_id = "1" # type 2 diabetes mellitus

    print(f"Testing heatmap generation for Drug {drug_id} + Disease {disease_id}...")

    try:
        print("\n--- Pathway Influence ---")
        pathway_data = compute_pathway_influence(drug_id, disease_id)
        print(json.dumps(pathway_data, indent=2))
        
        if not pathway_data.get("pathway_influence"):
            print("WARNING: Pathway influence data is empty!")
        else:
            print("SUCCESS: Pathway influence data generated.")

    except Exception as e:
        print(f"ERROR in Pathway Influence: {e}")

    try:
        print("\n--- Gene Match ---")
        gene_data = compute_gene_match(drug_id, disease_id)
        print(json.dumps(gene_data, indent=2))

        if not gene_data.get("gene_matches"):
            print("WARNING: Gene match data is empty!")
        else:
            print("SUCCESS: Gene match data generated.")

    except Exception as e:
        print(f"ERROR in Gene Match: {e}")

if __name__ == "__main__":
    test_heatmaps()
