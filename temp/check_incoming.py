
import pickle
import os
import sys

path = "c:/Users/kabhi/neurosymbolic/finalKG/data/graph_index.pkl"

def check():
    if not os.path.exists(path): return

    with open(path, "rb") as f:
        data = pickle.load(f)
    
    target = "869"
    incoming = 0
    sources = []
    
    for u in data:
        if target in data[u]:
            incoming += 1
            sources.append(u)
            if incoming > 5: break
            
    print(f"Metformin (869) Incoming Degree: {incoming}")
    if sources:
        print(f"Sample sources: {sources}")

if __name__ == "__main__":
    check()
