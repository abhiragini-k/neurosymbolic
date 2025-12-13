
import pickle
import os
import sys
import networkx as nx

# Add temp to path
sys.path.append(os.path.join(os.getcwd(), "temp"))

path = "c:/Users/kabhi/neurosymbolic/finalKG/data/graph_index.pkl"

def check():
    if not os.path.exists(path): return

    with open(path, "rb") as f:
        data = pickle.load(f) # Adjacency dict
    
    # Reconstruct graph object for nx functions if data is just dict
    # Wait, pickle contained a DiGraph object according to debug_empty_response.py output!
    # "Graph loaded. Type: networkx.classes.graph.DiGraph"
    
    G = data
    print(f"Graph loaded. Nodes: {len(G)}")
    
    source = "869"
    target = "1"
    
    if not G.has_node(source):
        print(f"Source {source} missing")
        return
    if not G.has_node(target):
         print(f"Target {target} missing")
         return
         
    G_undir = G.to_undirected()
    print("Converted to undirected.")
    
    if nx.has_path(G_undir, source, target):
        print("✅ Path EXISTS in Undirected Graph!")
        p = nx.shortest_path(G_undir, source, target)
        print(f"Path: {p}")
        
        # Also check Neighbors in Undirected
        print(f"Undir Degree Source: {G_undir.degree(source)}")
    else:
        print("❌ No path in Undirected Graph either.")

if __name__ == "__main__":
    check()
