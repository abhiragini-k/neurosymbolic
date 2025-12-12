import torch
from collections import defaultdict

# Load graph
# HeteroData requires weights_only=False or safe globals whitelist
graph = torch.load("data/graph.pt", weights_only=False)

print("\n================ EDGE VERIFICATION REPORT ================\n")

# Counters
forward_total = 0
reverse_total = 0
relation_counts = defaultdict(int)

for (src_type, rel, dst_type), edge_index in graph.edge_index_dict.items():
    num_edges = edge_index.shape[1]
    relation_counts[rel] += num_edges
    
    # Check reverse or forward
    if rel.endswith("_rev"):
        reverse_total += num_edges
    else:
        forward_total += num_edges

# Display summary
print("=== TOTALS ===")
print(f"Forward edges: {forward_total:,}")
print(f"Reverse edges: {reverse_total:,}")
print(f"Stored total edges: {forward_total + reverse_total:,}\n")

print("=== RELATION BREAKDOWN ===")
for rel, count in sorted(relation_counts.items(), key=lambda x: -x[1]):
    print(f"{rel:<25} : {count:,}")

print("\n==========================================================")
