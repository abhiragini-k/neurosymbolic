
import pickle
import os
import sys

# Add temp to path
sys.path.append(os.path.join(os.getcwd(), "temp"))

path = "c:/Users/kabhi/neurosymbolic/finalKG/data/graph_index.pkl"

def check():
    if not os.path.exists(path):
        print("Graph file missing")
        return

    with open(path, "rb") as f:
        data = pickle.load(f)
    
    # Check Metformin (6809)
    d_id = "6809"
    target_id = "1" # T2DM
    
    if d_id in data:
        print(f"Metformin ({d_id}) Neighbors: {list(data[d_id].keys())[:10]}")
        if target_id in data[d_id]:
            print(f"✅ EDGE FOUND: Metformin -> Diabetes ({target_id})")
            print(f"   Relation: {data[d_id][target_id]}")
        else:
            print(f"❌ NO DIRECT EDGE: Metformin -> Diabetes ({target_id})")
    else:
        print("Metformin not in graph.")
        
    # Check incoming to Diabetes
    # Since it's adj list, we have to scan all... expensive.
    # But wait, data is a dict of dicts? G[u][v]
    
    # Let's looking for ANY 'treats' edge from Metformin
    if d_id in data:
        for nbr, rel in data[d_id].items():
            if 'treats' in str(rel).lower():
                print(f"Metformin treats -> {nbr}")
                
if __name__ == "__main__":
    check()
