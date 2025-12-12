
import torch
from torch_geometric.data import HeteroData
import os
import sys

def validate_rgcn_readiness():
    graph_path = os.path.join('data', 'graph_with_embeddings.pt')
    
    print(f"Validating {graph_path} for R-GCN training...\n")
    
    if not os.path.exists(graph_path):
        print(f"FAIL: File not found at {graph_path}")
        return

    try:
        data = torch.load(graph_path, map_location='cpu', weights_only=False)
    except Exception as e:
        print(f"FAIL: Could not load graph. Error: {e}")
        return

    # Checks
    all_passed = True
    
    print("--- 1. Node Feature Check ---")
    # R-GCN needs features for all nodes (or use an embedding layer idx)
    # The requirement was to add 'x' embeddings [num_nodes, 128]
    
    total_nodes = 0
    for node_type in data.node_types:
        num_nodes = data[node_type].num_nodes
        total_nodes += num_nodes
        
        if 'x' not in data[node_type]:
            print(f"FAIL: Node type '{node_type}' is missing feature matrix 'x'.")
            all_passed = False
            continue
            
        x = data[node_type].x
        if x.shape != (num_nodes, 128):
            print(f"FAIL: Node type '{node_type}' feature shape mismatch. Expected ({num_nodes}, 128), got {x.shape}")
            all_passed = False
        else:
            print(f"PASS: {node_type:<20} | Nodes: {num_nodes:<6} | Emb: {str(list(x.shape)):<12} | Type: {x.dtype}")

    print(f"\nTotal Nodes: {total_nodes}")

    print("\n--- 2. Edge Connectivity Check ---")
    # Check if edge_index exists for all edge types
    total_edges = 0
    for edge_type in data.edge_types:
        if 'edge_index' not in data[edge_type]:
            print(f"FAIL: Edge type {edge_type} missing 'edge_index'")
            all_passed = False
            continue
            
        edge_index = data[edge_type].edge_index
        num_edges = edge_index.shape[1]
        total_edges += num_edges
        
        # Check validity of indices
        src_type, rel, dst_type = edge_type
        src_count = data[src_type].num_nodes
        dst_count = data[dst_type].num_nodes
        
        if num_edges > 0:
            if edge_index[0].max() >= src_count:
                print(f"FAIL: {edge_type} source index out of bounds. Max idx {edge_index[0].max()} >= {src_count}")
                all_passed = False
            if edge_index[1].max() >= dst_count:
                print(f"FAIL: {edge_type} dest index out of bounds. Max idx {edge_index[1].max()} >= {dst_count}")
                all_passed = False
        
        # print(f"PASS: {str(edge_type):<50} | Edges: {num_edges}") 
        # (Too many edge types to print all, just summary?)
    
    print(f"Checked {len(data.edge_types)} edge types. Total Edges: {total_edges}")

    print("\n--- 3. Metadata Structure ---")
    print(f"Node Types: {len(data.node_types)}")
    print(f"Edge Types: {len(data.edge_types)}")
    
    print("\n--- 4. Overall Status ---")
    if all_passed:
        status_msg = "SUCCESS: Graph structure and embeddings appear valid for R-GCN training.\nReady for: Message Passing, Link Prediction"
        print(status_msg)
    else:
        status_msg = "FAILURE: Critical issues found. See above for details."
        print(status_msg)
    
    # Save full report to file
    report_path = os.path.join('reports', 'rgcn_readiness_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        # We need to capture the prints. Ideally refactor, but for now just write the summary
        f.write(f"Validation Report for {graph_path}\n")
        f.write("="*50 + "\n\n")
        
        f.write("--- 1. Node Feature Check ---\n")
        for node_type in data.node_types:
            num_nodes = data[node_type].num_nodes
            if 'x' in data[node_type]:
                x = data[node_type].x
                f.write(f"PASS: {node_type:<25} | Nodes: {num_nodes:<10} | Emb: {str(list(x.shape)):<15} | Type: {x.dtype}\n")
            else:
                 f.write(f"FAIL: {node_type} missing features\n")
        
        f.write(f"\nTotal Nodes: {total_nodes}\n")
        
        f.write("\n--- 2. Edge Connectivity Check ---\n")
        f.write(f"Checked {len(data.edge_types)} edge types. Total Edges: {total_edges}\n")
        
        f.write("\n--- 3. Overall Status ---\n")
        f.write(status_msg + "\n")
        
    print(f"\nFull report saved to {report_path}")

if __name__ == "__main__":
    validate_rgcn_readiness()
