
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
        data = pickle.load(f) # This is a dict of adjacency lists based on my previous find
    
    # Wait, previous step said it's a DiGraph. Let's trust that.
    # checking type:
    print(f"Graph Type: {type(data)}")
    
    d_id = "869"
    dis_id = "1"
    
    if d_id in data:
        print(f"Drug {d_id}: Found. Neighbors (outgoing): {len(data[d_id])}")
    else:
        print(f"Drug {d_id}: NOT Found")
        
    if dis_id in data:
         print(f"Disease {dis_id}: Found. Neighbors (outgoing): {len(data[dis_id])}")
    else:
         print(f"Disease {dis_id}: NOT Found")
         
    # Check simple path existence directly if it is a graph
    import networkx as nx
    if isinstance(data, nx.Graph):
        if data.has_node(d_id) and data.has_node(dis_id):
            try:
                # Just check reachability
                has_path = nx.has_path(data, d_id, dis_id)
                print(f"Has path {d_id} -> {dis_id}: {has_path}")
            except Exception as e:
                print(f"Reachability check failed: {e}")
                
    # Now try polo
    print("Initializing Polo...")
    try:
        import polo_sci4
        agent = polo_sci4.TargetedAgent()
        print("Polo initialized.")
        paths = agent.explain(d_id, dis_id)
        print(f"Polo returned {len(paths)} paths.")
    except Exception as e:
        print(f"Polo failed: {e}")

if __name__ == "__main__":
    check()
