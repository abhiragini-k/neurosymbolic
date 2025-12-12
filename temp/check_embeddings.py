
import torch
import os
import sys

try:
    print("Loading graph.pt...")
    path = "c:/Users/kabhi/neurosymbolic/finalKG/data/graph.pt"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)
        
    data = torch.load(path)
    print("Graph loaded.")
    print(f"Data keys: {data.keys if hasattr(data, 'keys') else 'No keys attr'}")
    
    if hasattr(data, 'node_types'):
        print(f"Node types: {data.node_types}")
        if 'drug' in data.node_types:
            if hasattr(data['drug'], 'x') and data['drug'].x is not None:
                print(f"Drug embeddings shape: {data['drug'].x.shape}")
            else:
                print("Drug node type exists but has no 'x' attribute or it is None.")
                print(f"Drug attributes: {data['drug'].keys() if hasattr(data['drug'], 'keys') else 'No keys'}")
    else:
        print("Not a HeteroData object?")
        
except Exception as e:
    print(f"Error: {e}")
