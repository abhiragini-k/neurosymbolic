
import torch
import os
import sys

# Add local directory to path in case of custom classes
sys.path.append(os.getcwd())

try:
    print("Loading graph.pt with weights_only=False...")
    path = "c:/Users/kabhi/neurosymbolic/finalKG/data/graph.pt"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)
        
    # We must set weights_only=False because PyG Data objects are pickled
    data = torch.load(path, weights_only=False)
    print("Graph loaded successfully.")
    
    if hasattr(data, 'node_types'):
        print(f"Node types found: {data.node_types}")
        
        # Check for any variation of drug/compound
        for nt in data.node_types:
            print(f"--- Checking Node Type: {nt} ---")
            if hasattr(data[nt], 'x') and data[nt].x is not None:
                print(f"  Embeddings found! Shape: {data[nt].x.shape}")
            else:
                print(f"  No 'x' attribute.")
            
            # Print first few keys
            print(f"  Keys: {data[nt].keys() if hasattr(data[nt], 'keys') else 'No keys'}")
            
    else:
        print("Loaded object does not have 'node_types'.")
        print(type(data))
        
except Exception as e:
    print(f"Error: {e}")
