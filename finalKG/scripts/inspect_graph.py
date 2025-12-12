
import torch
from torch_geometric.data import HeteroData
import os

def inspect_graph():
    graph_path = os.path.join('data', 'graph.pt')
    if not os.path.exists(graph_path):
        print(f"File not found: {graph_path}")
        return

    try:
        # weights_only=False is required for PyG data objects
        # map_location='cpu' ensures we can load even if saved from GPU
        data = torch.load(graph_path, map_location='cpu', weights_only=False)
        print("Graph loaded successfully.")
        print(f"Node types: {data.node_types}")
        
        for node_type in data.node_types:
            print(f"\nNode Type: {node_type}")
            if 'x' in data[node_type]:
                print(f"  Features 'x' found. Shape: {data[node_type].x.shape}")
            else:
                print(f"  No features 'x' found.")
            
            if hasattr(data[node_type], 'num_nodes'):
                 print(f"  Num nodes: {data[node_type].num_nodes}")

    except Exception as e:
        print(f"Error loading graph: {e}")

if __name__ == "__main__":
    inspect_graph()
