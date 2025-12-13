
import pickle
import os
import sys

# Add temp to path
sys.path.append(os.path.join(os.getcwd(), "temp"))

path = "c:/Users/kabhi/neurosymbolic/finalKG/data/graph_index.pkl"

def check():
    if not os.path.exists(path): return

    with open(path, "rb") as f:
        data = pickle.load(f)
    
    # Metformin 6809, AMPK 23070
    d_id = "6809"
    g_id = "23070"
    
    if d_id in data:
        if g_id in data[d_id]:
            print(f"✅ EDGE FOUND: Metformin -> AMPK")
            print(f"   Rel: {data[d_id][g_id]}")
        else:
            print(f"❌ EDGE MISSING: Metformin -> AMPK")
            print(f"   Neighbors of Metformin: {list(data[d_id].keys())[:10]}")
    else:
        print("Metformin missing")

if __name__ == "__main__":
    check()
