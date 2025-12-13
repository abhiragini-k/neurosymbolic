
import pickle
import os

path = "c:/Users/kabhi/neurosymbolic/finalKG/data/graph_index.pkl"

if os.path.exists(path):
    try:
        with open(path, "rb") as f:
            data = pickle.load(f)
        
        print(f"Graph loaded. Number of nodes: {len(data)}")
        keys = list(data.keys())
        print(f"Sample keys: {keys[:10]}")
        
        # Check for Metformin (usually around ID 6809)
        # We need to know if keys are ints or strings
        
        metformin_id = "6809"
        if metformin_id in data:
            print(f"✅ Metformin ({metformin_id}) is in the graph.")
            neighbors = data[metformin_id]
            print(f"Metformin neighbors: {len(neighbors)}")
        else:
            print(f"❌ Metformin ({metformin_id}) NOT found in graph keys.")
            
    except Exception as e:
        print(f"Error loading pickle: {e}")
else:
    print("File not found.")
