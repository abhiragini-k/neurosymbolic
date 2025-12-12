import pandas as pd
import torch
from torch_geometric.data import HeteroData
import os
from utils import get_env_variable
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def construct_graph():
    data_dir = get_env_variable("DATA_DIR", "./data", required=False)
    
    nodes_path = os.path.join(data_dir, "nodes.csv")
    rels_path = os.path.join(data_dir, "relations.csv")
    
    if not os.path.exists(nodes_path) or not os.path.exists(rels_path):
        raise FileNotFoundError("Processed files not found. Run preprocess.py first.")

    logger.info("Loading processed data for graph construction...")
    nodes_df = pd.read_csv(nodes_path)
    rels_df = pd.read_csv(rels_path)

    data = HeteroData()

    # 1. Process Nodes
    # Group by label to determine node types
    # attributes: neo4j_id, label, name, identifier, new_id
    
    # We need to remap the global 'new_id' (which is 0..TotalNodes) to local IDs for each node type (0..NumTypeNodes)
    # PyG expects local indices for each node type.
    
    logger.info("Processing node types...")
    # Create a mapping from global_new_id -> (node_type, local_id)
    global_to_local_map = {}
    
    for node_type, group in nodes_df.groupby('label'):
        # sort by new_id to ensure deterministic ordering if needed, 
        # but simpler is just to assign 0..N based on the group
        group = group.sort_values('new_id').reset_index(drop=True)
        
        # Add metadata
        data[node_type].num_nodes = len(group)
        # Store original IDs as a feature or property if needed for lookup
        # data[node_type].node_ids = torch.tensor(group['new_id'].values) # global IDs
        
        # We need to build the map for edges
        # group['new_id'] is the global ID from preprocess.py
        # index is the local ID
        local_ids = group.index.values
        global_ids = group['new_id'].values
        
        for g_id, l_id in zip(global_ids, local_ids):
            global_to_local_map[g_id] = (node_type, l_id)

    logger.info(f"Identified node types: {list(data.node_types)}")

    # 2. Process Edges
    # We need to split edges by (SourceType, RelationType, TargetType)
    
    logger.info("Processing relationships...")
    
    # We need to iterate and re-map
    # This might be slow for millions of edges if done purely in python loop.
    # Vectorized approach:
    # Add node types and logical IDs to the relationships dataframe based on the map.
    
    # It's faster to map the dataframe columns.
    # But dictionary map is efficient enough for 2M items usually. 
    # Let's map global IDs to (Type, LocalID).
    
    # To do this efficiently with pandas:
    # We can join/merge, but 'nodes_df' has the type info.
    
    # Let's create a lookup series/df
    nodes_lookup = nodes_df.set_index('new_id')[['label']]
    # Helper to get local count per type to calculate local IDs? 
    # Actually, we already did the group sort.
    # Let's add 'local_id' to nodes_df
    nodes_df['local_id'] = nodes_df.groupby('label').cumcount()
    
    # Merge source info
    rels_df = rels_df.merge(nodes_df[['new_id', 'label', 'local_id']], left_on='source_new_id', right_on='new_id', suffixes=('', '_source'))
    rels_df = rels_df.rename(columns={'label': 'source_type', 'local_id': 'source_local_id'})
    
    # Merge target info
    rels_df = rels_df.merge(nodes_df[['new_id', 'label', 'local_id']], left_on='target_new_id', right_on='new_id', suffixes=('', '_target'))
    rels_df = rels_df.rename(columns={'label': 'target_type', 'local_id': 'target_local_id'})
    
    # Now group by (source_type, type, target_type)
    edge_groups = rels_df.groupby(['source_type', 'type', 'target_type'])
    
    for (src_type, rel_type, dst_type), group in edge_groups:
        src = torch.tensor(group['source_local_id'].values, dtype=torch.long)
        dst = torch.tensor(group['target_local_id'].values, dtype=torch.long)
        
        # 1. Forward Edge: (Source, Relation, Target)
        data[src_type, rel_type, dst_type].edge_index = torch.stack([src, dst], dim=0)
        
        # 2. Reverse Edge: (Target, Relation_rev, Source)
        # We assume reverse relation name is simply rel_type + "_rev"
        # We flip src and dst tensors
        rev_rel_type = f"{rel_type}_rev"
        data[dst_type, rev_rel_type, src_type].edge_index = torch.stack([dst, src], dim=0)

    logger.info(f"Graph construction complete. {len(data.edge_types)} edge types.")
    return data

if __name__ == "__main__":
    # Test run
    try:
        g = construct_graph()
        print(g)
    except Exception as e:
        logger.error(e)
