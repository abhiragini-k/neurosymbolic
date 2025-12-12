import pandas as pd
import os
from utils import get_env_variable
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def preprocess_data():
    data_dir = get_env_variable("DATA_DIR", "./data", required=False)
    
    raw_nodes_path = os.path.join(data_dir, "raw_nodes.csv")
    raw_edges_path = os.path.join(data_dir, "raw_edges.csv")
    
    if not os.path.exists(raw_nodes_path) or not os.path.exists(raw_edges_path):
        logger.error("Raw data files not found. Run hetionet_extract.py first.")
        return

    logger.info("Loading raw data...")
    nodes_df = pd.read_csv(raw_nodes_path)
    edges_df = pd.read_csv(raw_edges_path)
    
    logger.info(f"Loaded {len(nodes_df)} nodes and {len(edges_df)} edges.")

    # 1. Map Node IDs to continuous integers
    # We'll create a mapping from neo4j_id to new_id (0 to N-1)
    # It's useful to keep track of the original Neo4j ID for debugging
    nodes_df['new_id'] = range(len(nodes_df))
    
    # Create a mapping dictionary
    id_map = dict(zip(nodes_df['neo4j_id'], nodes_df['new_id']))
    
    # 2. Save processed nodes
    processed_nodes_path = os.path.join(data_dir, "nodes.csv")
    nodes_df.to_csv(processed_nodes_path, index=False)
    logger.info(f"Saved processed nodes to {processed_nodes_path}")
    
    # 3. Process Edges
    # Map source and target IDs to new_ids
    edges_df['source_new_id'] = edges_df['source_id'].map(id_map)
    edges_df['target_new_id'] = edges_df['target_id'].map(id_map)
    
    # Drop rows where mapping failed (if any, shouldn't happen if consistency is maintained)
    edges_df.dropna(subset=['source_new_id', 'target_new_id'], inplace=True)
    edges_df['source_new_id'] = edges_df['source_new_id'].astype(int)
    edges_df['target_new_id'] = edges_df['target_new_id'].astype(int)
    
    # Save processed edges
    processed_edges_path = os.path.join(data_dir, "relations.csv")
    edges_df[['source_new_id', 'target_new_id', 'type']].to_csv(processed_edges_path, index=False)
    logger.info(f"Saved processed edges to {processed_edges_path}")

    # 4. Create triples.txt (Head, Relation, Tail)
    # The format depends on what the user wants, usually tab-separated or space-separated names or IDs.
    # The user asked for "triples.txt". Usually, this means symbolic names for knowledge graph embeddings,
    # or IDs. Given the "preprocessing" context for R-GCN, integer IDs are better for PyG, 
    # but "triples.txt" often implies a format for tools like KGE libraries which might want strings.
    # REQUIRED: "Convert exported triples into PyTorch Geometric HeteroData".
    # I will provide a triples.txt with the mapped integer IDs and Relation Types for clarity/portability.
    
    triples_path = os.path.join(data_dir, "triples.txt")
    with open(triples_path, 'w') as f:
        for _, row in edges_df.iterrows():
            f.write(f"{row['source_new_id']}\t{row['type']}\t{row['target_new_id']}\n")
            
    logger.info(f"Saved triples to {triples_path}")

if __name__ == "__main__":
    preprocess_data()
