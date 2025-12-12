from utils import get_neo4j_driver
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def check_counts():
    driver = get_neo4j_driver()
    
    query_nodes = """
    MATCH (n)
    RETURN head(labels(n)) as label, count(n) as count
    ORDER BY count DESC
    """
    
    query_edges = """
    MATCH ()-[r]->()
    RETURN type(r) as type, count(r) as count
    ORDER BY count DESC
    """
    
    try:
        with driver.session() as session:
            print("\n=== Node Counts ===")
            result = session.run(query_nodes)
            total_nodes = 0
            for record in result:
                label = record['label'] if record['label'] else "No Label"
                count = record['count']
                total_nodes += count
                print(f"{label:<25} : {count:,}")
            print(f"{'-'*40}")
            print(f"{'TOTAL NODES':<25} : {total_nodes:,}")

            print("\n=== Relationship Counts ===")
            result = session.run(query_edges)
            total_edges = 0
            for record in result:
                rtype = record['type']
                count = record['count']
                total_edges += count
                print(f"{rtype:<25} : {count:,}")
            print(f"{'-'*40}")
            print(f"{'TOTAL EDGES':<25} : {total_edges:,}")
            
    except Exception as e:
        logger.error(f"Error checking DB: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    check_counts()
