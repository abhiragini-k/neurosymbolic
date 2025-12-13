import sys
import os
import time

print("Starting import checks...")

start = time.time()
try:
    import torch
    print(f"Imported torch in {time.time() - start:.2f}s")
except Exception as e:
    print(f"Failed to import torch: {e}")

start = time.time()
try:
    from torch_geometric.nn import RGCNConv
    print(f"Imported torch_geometric in {time.time() - start:.2f}s")
except Exception as e:
    print(f"Failed to import torch_geometric: {e}")

sys.path.append(os.getcwd())
start = time.time()
try:
    from explainability import gnn_service
    print(f"Imported gnn_service in {time.time() - start:.2f}s")
except Exception as e:
    print(f"Failed to import gnn_service: {e}")
