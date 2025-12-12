import csv
import os
from utils import get_neo4j_driver, get_env_variable
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_data():
    driver = get_neo4j_driver()
    data_dir = get_env_variable("DATA_DIR", "./data", required=False)
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    logger.info(f"Extracting Neo4j data to {data_dir}...")
    
    # query for nodes
    # We extract ID, labels (taking the first one for simplicity as Hetionet nodes usually have one primary label), and name/id property
    node_query = """
    MATCH (n)
    RETURN id(n) as neo4j_id, labels(n) as labels, n.name as name, n.identifier as identifier
    """
    
    nodes_file = os.path.join(data_dir, "raw_nodes.csv")
    logger.info(f"Extracting nodes to {nodes_file}...")
    
    try:
        with driver.session() as session:
            with open(nodes_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['neo4j_id', 'label', 'name', 'identifier'])
                
                result = session.run(node_query)
                count = 0
                for record in result:
                    # Neo4j labels are a list, we take the first one or join them
                    labels = list(record['labels'])
                    label = labels[0] if labels else 'Unknown'
                    writer.writerow([record['neo4j_id'], label, record['name'], record['identifier']])
                    count += 1
                logger.info(f"Extracted {count} nodes.")

    except Exception as e:
        logger.error(f"Error extracting nodes: {e}")
        return

    # query for relationships
    # We extract source ID, target ID, and relationship type
    # FILTER: Only include specific Drug Repurposing relations + Backbone
    rel_filter = [
        'treats', 'palliates',                  # Drug-Disease
        'upregulates', 'downregulates', 'binds', 'expresses', # Drug-Gene
        'causes',                               # Drug-SideEffect
        'presents',                             # Disease-Symptom
        'participates', 'regulates', 'interacts', 'covaries' # Backbone
    ]
    
    rel_query = f"""
    MATCH (s)-[r]->(t)
    WHERE type(r) IN {rel_filter}
    RETURN id(s) as source_id, type(r) as type, id(t) as target_id
    """
    
    rels_file = os.path.join(data_dir, "raw_edges.csv")
    logger.info(f"Extracting edges to {rels_file}...")
    
    try:
        with driver.session() as session:
            with open(rels_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['source_id', 'type', 'target_id'])
                
                result = session.run(rel_query)
                count = 0
                for record in result:
                    writer.writerow([record['source_id'], record['type'], record['target_id']])
                    count += 1
                logger.info(f"Extracted {count} edges.")

    except Exception as e:
        logger.error(f"Error extracting edges: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    extract_data()
