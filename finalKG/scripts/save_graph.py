import torch
import os
from build_graph import construct_graph
from utils import get_env_variable
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_graph_to_disk():
    data_dir = get_env_variable("DATA_DIR", "./data", required=False)
    output_path = os.path.join(data_dir, "graph.pt")
    
    logger.info("Building graph...")
    data = construct_graph()
    
    logger.info(f"Saving graph to {output_path}...")
    torch.save(data, output_path)
    
    logger.info("Done.")

if __name__ == "__main__":
    save_graph_to_disk()
