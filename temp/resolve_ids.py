
import json
import pickle
import os
import sys

# Add temp to path
sys.path.append(os.path.join(os.getcwd(), "temp"))

def check():
    # Load Mapping
    with open("c:/Users/kabhi/neurosymbolic/backend/compound_id_to_name.json", "r") as f:
        c_map = json.load(f)
        
    metformin_id = None
    for k, v in c_map.items():
        if v.lower() == "metformin":
            metformin_id = k
            print(f"Found Metformin: ID {k}")
            break
            
    if not metformin_id:
        print("Metformin NOT found in mapping file.")
        
    if "869" in c_map:
        print(f"ID 869 is: {c_map['869']}")
    else:
        print("ID 869 NOT found in mapping.")

    # Load Graph
    g_path = "c:/Users/kabhi/neurosymbolic/finalKG/data/graph_index.pkl"
    if os.path.exists(g_path):
        with open(g_path, "rb") as f:
            data = pickle.load(f)  # Adjacency dict
            
        # Check Metformin connectivity
        if metformin_id:
            if metformin_id in data:
                out_degree = len(data[metformin_id])
                print(f"Metformin ({metformin_id}) Out-Degree: {out_degree}")
            else:
                 print(f"Metformin ({metformin_id}) NOT in graph nodes.")

        # Check 869 connectivity
        if "869" in data:
            print(f"ID 869 Out-Degree: {len(data['869'])}")
        else:
             print(f"ID 869 NOT in graph nodes.")
             
    else:
        print("Graph pickle missing.")

if __name__ == "__main__":
    check()
