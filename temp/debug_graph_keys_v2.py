
import pickle
import os

path = "c:/Users/kabhi/neurosymbolic/finalKG/data/graph_index.pkl"

if os.path.exists(path):
    try:
        with open(path, "rb") as f:
            data = pickle.load(f)
        
        print(f"Graph loaded.")
        print(f"Type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"Number of nodes: {len(data)}")
            keys = list(data.keys())
            print(f"Sample keys: {keys[:10]}")
            if "metformin" in keys or "6809" in keys: print("Metformin found")
        elif isinstance(data, list):
            print(f"List length: {len(data)}")
            print(f"Sample items: {data[:5]}")
        else:
            print(f"Unknown type: {type(data)}")
            
    except Exception as e:
        print(f"Error loading pickle: {e}")
else:
    print("File not found.")
