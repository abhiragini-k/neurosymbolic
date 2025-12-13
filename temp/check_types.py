
import torch
import sys
import os

sys.path.append(os.getcwd())

files = [
    "c:/Users/kabhi/neurosymbolic/finalKG/data/graph.pt",
    "c:/Users/kabhi/neurosymbolic/R-GCN-MODEL/graph.pt"
]

for p in files:
    print(f"Checking {p}...")
    if not os.path.exists(p):
        print("  Not found.")
        continue
    try:
        data = torch.load(p, weights_only=False)
        print(f"  Node types: {data.node_types}")
        for nt in data.node_types:
            if hasattr(data[nt], 'x') and data[nt].x is not None:
                print(f"    {nt}: x shape {data[nt].x.shape}")
    except Exception as e:
        print(f"  Error: {e}")
