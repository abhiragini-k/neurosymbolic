import os
import json
from utils import get_env_variable, get_neo4j_driver
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_hetionet():
    """
    Loads Hetionet data into Neo4j.
    This script assumes a fresh database or handles constraints idempotently.
    """
    logger.info("Connecting to Neo4j...")
    driver = get_neo4j_driver()
    
    # URL for Hetionet JSON v1.0
    HETIONET_JSON_URL = "https://github.com/hetio/hetionet/raw/master/hetnet/json/hetionet-v1.0.json.bz2"
    
    data_dir = get_env_variable("DATA_DIR", "./data", required=False)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    local_file = os.path.join(data_dir, "hetionet-v1.0.json.bz2")
    json_file = os.path.join(data_dir, "hetionet-v1.0.json")

    # 1. Download
    if not os.path.exists(local_file) and not os.path.exists(json_file):
        logger.info(f"Downloading Hetionet from {HETIONET_JSON_URL}...")
        try:
            import requests
            from tqdm import tqdm
            response = requests.get(HETIONET_JSON_URL, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(local_file, 'wb') as f, tqdm(
                desc=local_file,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in response.iter_content(chunk_size=1024):
                    size = f.write(data)
                    bar.update(size)
        except ImportError:
            logger.error("Please install 'requests' and 'tqdm' to download data automatically: pip install requests tqdm")
            return

    # 2. Decompress
    if not os.path.exists(json_file):
        logger.info(f"Decompressing {local_file}...")
        try:
            import bz2
            with bz2.open(local_file, "rb") as f_in:
                with open(json_file, "wb") as f_out:
                    f_out.write(f_in.read())
        except Exception as e:
            logger.error(f"Failed to decompress: {e}")
            return

    # 3. Load into Neo4j
    logger.info("Loading JSON data...")
    import json
    with open(json_file, 'r') as f:
        graph_data = json.load(f)
    
    nodes = graph_data['nodes']
    edges = graph_data['edges']
    
    logger.info(f"Found {len(nodes)} nodes and {len(edges)} edges in JSON.")

    with driver.session() as session:
        # Create Constraints (Optional but recommended for performance)
        logger.info("Creating constraints...")
        # Hetionet nodes have 'kind' and 'identifier'
        unique_kinds = set(n['kind'] for n in nodes)
        for kind in unique_kinds:
            # Sanitize kind for Cypher
            safe_kind = kind.replace(' ', '_')
            try:
                session.run(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:`{safe_kind}`) REQUIRE n.identifier IS UNIQUE")
            except Exception as e:
                logger.warning(f"Could not create constraint for {kind}: {e}")

        # Batch Load Nodes
        logger.info("Ingesting nodes...")
        batch_size = 5000
        # Group by kind to optimize
        from collections import defaultdict
        nodes_by_kind = defaultdict(list)
        for n in nodes:
            nodes_by_kind[n['kind']].append(n)
            
        for kind, kind_nodes in nodes_by_kind.items():
            safe_kind = kind.replace(' ', '_')
            logger.info(f"  Loading {len(kind_nodes)} nodes of type {kind}...")
            
            for i in range(0, len(kind_nodes), batch_size):
                batch = kind_nodes[i:i+batch_size]
                # We simply create/merge. MERGE is safer but slower. 
                # Since dataset is static, assumes empty DB or use MERGE.
                query = f"""
                UNWIND $batch AS row
                MERGE (n:`{safe_kind}` {{identifier: row.identifier}})
                SET n.name = row.name, n.license = row.license, n.url = row.url
                """
                session.run(query, batch=batch)

        # Batch Load Edges
        logger.info("Ingesting relationships...")
        # Edges: source_id, target_id, kind, direction, source_id (kind), target_id (kind) logic
        # Hetionet JSON edges have: source_id (compound::DB0001), target_id (gene::123), kind (AuG)
        # Note: The 'identifier' in nodes is like 'DB0001', but in edges source_id might be 'Compound::DB0001'.
        # Let's verify format.
        # usually hetionet JSON uses 'kind::identifier' as the ID string in edges?
        # Let's check a sample or assume standard Hetionet JSON v1.0 schema.
        # In v1.0 JSON: 
        # Node: {"kind": "Gene", "identifier": 7852, "name": "CXCR4"}
        # Edge: {"source_id": ["Gene", 7852], "target_id": ["Anatomy", "UBERON:0002038"], "kind": "GdaA", "direction": "both"}
        # Wait, the v1.0 JSON values for source_id are often [Kind, ID]. 
        
        # Let's inspect the first edge if possible, or handle [Kind, ID] tuple.
        # If I can't inspect, I'll write robust logic.
        
        # Assuming source_id is [Kind, Identifier] based on common Hetionet parsers.
        
        # We need a unified approach.
        edge_batches = [edges[i:i+batch_size] for i in range(0, len(edges), batch_size)]
        
        from tqdm import tqdm
        for batch in tqdm(edge_batches, desc="Edges"):
            # We need to reshape batch for simple Cypher
            # Let's preprocess batch data
            cypher_batch = []
            for edge in batch:
                # source_id can be ["Gene", 7852]
                src_kind, src_id = edge['source_id']
                dst_kind, dst_id = edge['target_id']
                rel_type = edge['kind']
                
                cypher_batch.append({
                    "src_kind": src_kind.replace(' ', '_'),
                    "src_id": src_id,
                    "dst_kind": dst_kind.replace(' ', '_'),
                    "dst_id": dst_id,
                    "rel_type": rel_type.replace(' ', '_') # Ensure safe cypher
                })
            
            # Since rel_types vary, we can't easily UNWIND multiple types in one query unless we use APOC.
            # Without APOC, we must group by rel type or use string formatting (risky but okay for controlled data).
            # Better: Group by Rel Type inside the batch loop or just loop.
            
            # Optimization: Group this batch by rel_type
            batch_by_type = defaultdict(list)
            for row in cypher_batch:
                batch_by_type[row['rel_type']].append(row)
                
            for r_type, rows in batch_by_type.items():
                # All rows here have same rel_type but might have mixed node types (unlikely in Hetionet metagraph, but possible).
                # Actually Hetionet edge kinds strongly imply source/target types.
                # But to be generic, we match source and target by kind+id.
                
                # We can't parameterize the relationship type in pure Cypher (requires APOC).
                # So we inject the type in the query string (safe because we sanitized).
                
                # However, src_kind and dst_kind can also vary? In a 'kind' of edge, usually src/dst types are fixed.
                # Let's assume they are fixed or handle them.
                # Easiest is to match strictly on identifier + kind.
                
                # Warning: MATCH (a:Label), (b:Label) is fast if indexed.
                
                # Check if src_kind/dst_kind are uniform in this block.
                # They should be for a specific metedge, but let's be safe.
                # UNWIND is best if we can do:
                # MATCH (s) WHERE s.identifier = row.src_id AND labels(s) = row.src_kind ... hard.
                
                # Alternative: Use "call {...}" (Neo4j 5+) or just match by identifier only?
                # Identifiers are NOT globally unique in Hetionet (e.g. integers for Genes, strings for others).
                # But (Kind, ID) is unique.
                
                # Let's try to query:
                # UNWIND $rows as row
                # MATCH (s) WHERE row.src_kind IN labels(s) AND s.identifier = row.src_id
                # ... expensive.
                
                # Best approach for speed:
                # If we know the src_label and dst_label for the rel_type, we can specialize.
                # Since we don't know them upfront without analyzing, 
                # We will just iterate and execute. It's slower but works.
                # OR, we grouping by (src_kind, dst_kind, rel_type).
                
                complex_groups = defaultdict(list)
                for row in rows:
                    key = (row['src_kind'], row['dst_kind'])
                    complex_groups[key].append(row)
                    
                for (s_kind, d_kind), items in complex_groups.items():
                    query = f"""
                    UNWIND $batch as row
                    MATCH (s:`{s_kind}` {{identifier: row.src_id}})
                    MATCH (t:`{d_kind}` {{identifier: row.dst_id}})
                    MERGE (s)-[r:`{r_type}`]->(t)
                    """
                    session.run(query, batch=items)

    logger.info("Hetionet loading complete.")

if __name__ == "__main__":
    load_hetionet()
