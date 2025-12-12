import pandas as pd
import json
import os
import sys

def generate_mappings():
    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    nodes_path = os.path.join(base_dir, "data", "nodes.csv")
    
    # Output paths (target: backend directory)
    backend_dir = os.path.abspath(os.path.join(base_dir, "..", "backend"))
    compound_out = os.path.join(backend_dir, "compound_id_to_name.json")
    disease_out = os.path.join(backend_dir, "disease_id_to_name.json")

    print(f"Reading nodes from: {nodes_path}")
    if not os.path.exists(nodes_path):
        print("Error: nodes.csv not found!")
        return

    df = pd.read_csv(nodes_path)
    
    # Process Compounds
    print("Processing Compounds...")
    compounds = df[df['label'] == 'Compound'].copy()
    # Sort by new_id to ensure alignment with graph.pt/npy indices
    compounds = compounds.sort_values('new_id')
    # Create local index (0 to N-1)
    # The 'npy' matrix indices correspond to these sorted positions
    compound_mapping = {}
    for local_idx, row in enumerate(compounds.itertuples()):
        # row.name is the actual name column content
        name = getattr(row, 'name', 'Unknown')
        compound_mapping[str(local_idx)] = name
        
    with open(compound_out, 'w') as f:
        json.dump(compound_mapping, f, indent=2)
    print(f"Saved {len(compound_mapping)} compounds to {compound_out}")

    # Process Diseases
    print("Processing Diseases...")
    diseases = df[df['label'] == 'Disease'].copy()
    diseases = diseases.sort_values('new_id')
    
    disease_mapping = {}
    for local_idx, row in enumerate(diseases.itertuples()):
        name = getattr(row, 'name', 'Unknown')
        disease_mapping[str(local_idx)] = name
        
    with open(disease_out, 'w') as f:
        json.dump(disease_mapping, f, indent=2)
    print(f"Saved {len(disease_mapping)} diseases to {disease_out}")

if __name__ == "__main__":
    generate_mappings()
