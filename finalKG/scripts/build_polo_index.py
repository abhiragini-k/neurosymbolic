import networkx as nx
import pandas as pd
import pickle
import os
import logging
from utils import get_env_variable

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def build_nx_graph():
    """
    Builds a NetworkX graph from processed CSVs and pickles it for the Polo Agent.
    """
    data_dir = get_env_variable("DATA_DIR", "./data", required=False)
    
    nodes_path = os.path.join(data_dir, "nodes.csv")
    rels_path = os.path.join(data_dir, "relations.csv")
    output_path = os.path.join(data_dir, "graph_index.pkl")

    if not os.path.exists(nodes_path) or not os.path.exists(rels_path):
        logger.error("Processed data (nodes.csv/relations.csv) not found. Run preprocess.py first.")
        return

    logger.info("Loading CSVs...")
    nodes_df = pd.read_csv(nodes_path)
    rels_df = pd.read_csv(rels_path)

    logger.info("Building NetworkX Graph...")
    # Initialize Directed Graph
    G = nx.DiGraph()

    # Add Nodes
    # Expects columns: new_id, name, label, identifier
    for _, row in nodes_df.iterrows():
        # Polo agent uses string IDs usually, but let's check backend compatibility.
        # backend/polo_sci4.py: loads pickle. If 'nodes' attr exists, uses it. 
        # else iterates items().
        # self.nodes = {} populated from nodes.csv separately in polo_sci4.
        # But here we should store struct?
        # Polo expects: self.DirectedG = loaded_obj
        # self.G = self.DirectedG.to_undirected()
        
        # We'll use the 'new_id' (int) converted to str as the node ID to match standard usage, 
        # or keep int if the rest of pipeline uses int.
        # R-GCN uses int. Polo uses whatever is in graph_index.pkl.
        # Let's stick to stringified new_id to be safe for JSON compatibility downstream, 
        # or int if that's what was there. 
        # Checking existing nodes.csv: it has new_id. 
        # Let's use string keys to be safe.
        
        nid = str(row['new_id'])
        G.add_node(nid, name=row['name'], type=row['label'])

    logger.info(f"Added {G.number_of_nodes()} nodes.")

    # Add Edges
    # columns: source_new_id, target_new_id, type
    for _, row in rels_df.iterrows():
        src = str(row['source_new_id'])
        dst = str(row['target_new_id'])
        rel = row['type']
        
        G.add_edge(src, dst, relation=rel)

    logger.info(f"Added {G.number_of_edges()} edges.")
    
    logger.info(f"Saving to {output_path}...")
    with open(output_path, "wb") as f:
        pickle.dump(G, f)
        
    logger.info("Done.")

if __name__ == "__main__":
    build_nx_graph()
