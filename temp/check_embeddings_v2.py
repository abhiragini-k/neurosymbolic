
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
        print(f"Node types: {data.node_types}")
        if 'drug' in data.node_types:
            if hasattr(data['drug'], 'x') and data['drug'].x is not None:
                print(f"Drug embeddings shape: {data['drug'].x.shape}")
                print("SUCCESS: Embeddings found for 'drug'.")
            else:
                print("Drug node type exists but has no 'x' attribute or it is None.")
        else:
             print("Drug node type not found.")
    else:
        print("Loaded object does not have 'node_types'. Is it a PyG HeteroData object?")
        print(type(data))
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
