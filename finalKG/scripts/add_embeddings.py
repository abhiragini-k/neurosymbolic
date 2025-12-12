
import torch
from torch_geometric.data import HeteroData
import os

def add_embeddings():
    input_path = os.path.join('data', 'graph.pt')
    output_path = os.path.join('data', 'graph_with_embeddings.pt')
    report_path = os.path.join('reports', 'embedding_verification.txt')
    
    # Ensure reports directory exists
    os.makedirs('reports', exist_ok=True)

    if not os.path.exists(input_path):
        print(f"Error: Input file found: {input_path}")
        return

    try:
        # Load graph
        print(f"Loading graph from {input_path}...")
        data = torch.load(input_path, map_location='cpu', weights_only=False)
        
        verification_lines = []
        header = f"{'Node Type':<25} | {'Num Nodes':<10} | {'Feature Shape':<15} | {'Status'}"
        print("-" * 70)
        print(header)
        print("-" * 70)
        verification_lines.append(header)
        verification_lines.append("-" * 70)

        for node_type in data.node_types:
            num_nodes = data[node_type].num_nodes
            
            # Check if x exists
            if 'x' not in data[node_type]:
                # Create random embeddings
                data[node_type].x = torch.randn(num_nodes, 128)
                status = "Added"
            else:
                # If exists, check shape
                if data[node_type].x.shape[1] != 128:
                    # Overwrite if shape mismatch? User said "Patch missing". 
                    # But user also said "Fail with error if shape mismatch occurs".
                    # Let's interpret "Fail with error if shape mismatch occurs" as checking AFTER we tried to ensure they exist.
                    # Or maybe checking existing ones. 
                    # "If x does not already exist -> create it" implies we leave existing ones alone unless they are wrong?
                    # "Fail with error" implies strict validation.
                    # If existing shape is wrong, we should prob fail or warn. 
                    # Given instructions "If x does not already exist -> create it", I will create if missing. 
                    # If present, I will validate.
                    status = f"Existing ({data[node_type].x.shape})"
                else:
                    status = "Existing (Verified)"
            
            # Sub-step verification
            feat_shape = str(list(data[node_type].x.shape))
            
            line = f"{node_type:<25} | {num_nodes:<10} | {feat_shape:<15} | {status}"
            print(line)
            verification_lines.append(line)

            # Validation Rules
            if data[node_type].x is None:
                 raise ValueError(f"Node type {node_type} has no features!")
            
            if data[node_type].x.shape != (num_nodes, 128):
                 raise ValueError(f"Shape mismatch for {node_type}: Expected ({num_nodes}, 128), got {data[node_type].x.shape}")

        print("-" * 70)
        
        # Save
        print(f"Saving updated graph to {output_path}...")
        torch.save(data, output_path)
        print("Save complete.")

        # Write report
        with open(report_path, 'w') as f:
            f.write("\n".join(verification_lines))
        print(f"Verification report saved to {report_path}")

    except Exception as e:
        print(f"Error: {e}")
        # Write failure to report as well if possible
        with open(report_path, 'w') as f:
            f.write(f"FAILED: {e}")
        exit(1)

if __name__ == "__main__":
    add_embeddings()
