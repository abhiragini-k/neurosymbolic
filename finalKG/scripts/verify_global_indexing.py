import torch
import torch_geometric
import sys
import os

# Set absolute path for safety or rely on relative
# User specified: data/graph_with_embeddings.pt
DATA_PATH = "data/graph_with_embeddings.pt"
REPORT_PATH = "reports/global_index_verification.txt"

def main():
    report_lines = []
    
    def log(line):
        print(line)
        report_lines.append(line)

    # 1. Load data
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found.")
        sys.exit(1)
        
    try:
        data = torch.load(DATA_PATH, weights_only=False)
    except TypeError:
        try:
             data = torch.load(DATA_PATH)
        except Exception as e:
             print(f"Error loading {DATA_PATH}: {e}")
             sys.exit(1)
    except Exception as e:
        print(f"Error loading {DATA_PATH}: {e}")
        sys.exit(1)

    log("✅ GLOBAL INTEGER INDEX VALIDATION REPORT")
    log("========================================")

    # 2. Node Validation
    node_counts = {}
    
    for node_type in data.node_types:
        store = data[node_type]
        if hasattr(store, 'num_nodes') and store.num_nodes is not None:
            count = store.num_nodes
        elif hasattr(store, 'x') and store.x is not None:
            count = store.x.size(0)
        else:
            count = store.num_nodes if store.num_nodes is not None else 0
            
        node_counts[node_type] = count
        
        log(f"{node_type:<9} | {count:<5} | [0 ... {count-1}]")

    log("----------------------------------------")

    # 3. Edge Validation
    any_check_failed = False
    
    for edge_type in data.edge_types:
        src_type, relation, dst_type = edge_type
            
        edge_store = data[edge_type]
        edge_index = edge_store.edge_index
        
        num_src = node_counts.get(src_type, 0)
        num_dst = node_counts.get(dst_type, 0)
        
        if edge_index.numel() > 0:
            max_src = int(edge_index[0].max())
            max_dst = int(edge_index[1].max())
            status_bool = (max_src < num_src) and (max_dst < num_dst)
        else:
            max_src = -1
            max_dst = -1
            status_bool = True
            
        status_str = "✅ VALID" if status_bool else "❌ FAIL"
        
        rel_str = f"{src_type} -[{relation}]-> {dst_type}"
        line = (f"{rel_str} | {max_src} < {num_src} | {max_dst} < {num_dst} | {status_str}")
        log(line)
        
        if not status_bool:
            any_check_failed = True
            break
            
    log("----------------------------------------")
    
    if not any_check_failed:
        log("✅ ALL GLOBAL INDICES ARE VALID FOR BACKEND INFERENCE")
    
    # 5. Save report
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    # 6. Fail if needed
    if any_check_failed:
        raise RuntimeError("Validation failed. See output.")

if __name__ == "__main__":
    main()
