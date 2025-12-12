import sys
import os
from typing import List, Dict, Any

# Add temp directory to path to import polo_sci4
TEMP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../temp"))
sys.path.append(TEMP_DIR)

from polo_sci4 import TargetedAgent

class NeurosymbolicService:
    def __init__(self):
        self.agent = None
        self._initialize_agent()

    def _initialize_agent(self):
        try:
            nodes_path = os.path.join(TEMP_DIR, "nodes.csv")
            graph_path = os.path.join(TEMP_DIR, "graph_index.pkl")
            
            if os.path.exists(nodes_path) and os.path.exists(graph_path):
                print(f"Initializing Neurosymbolic Agent with data from {TEMP_DIR}")
                self.agent = TargetedAgent(nodes_path=nodes_path, graph_path=graph_path)
            else:
                print(f"Warning: Neurosymbolic data files not found in {TEMP_DIR}")
        except Exception as e:
            print(f"Error initializing Neurosymbolic Agent: {e}")

    def get_explanation(self, drug_id: str, disease_id: str) -> List[Dict[str, Any]]:
        """
        Generates an explanation path between a drug and a disease.
        Returns a list of paths with scores and tags.
        """
        if not self.agent:
            # Try to re-initialize if failed previously
            self._initialize_agent()
            
        if not self.agent:
            raise ValueError("Neurosymbolic Agent is not initialized.")

        # Ensure IDs are strings as expected by the agent (e.g., "Compound::123")
        # The agent logic seems to strip prefixes, but let's pass what it expects or raw IDs if that's what it takes.
        # polo_sci4.py: clean = n_id.split("::")[-1] -> checks self.nodes.get(clean)
        # So passing "123" or "Compound::123" both work if "123" is the key in nodes.
        
        # The agent.explain method returns the found_paths list.
        # It also saves viz_data.json to the current working directory, which might be backend/
        # We might want to control that, but for now let's let it run.
        
        return self.agent.explain(drug_id, disease_id)

neurosymbolic_service = NeurosymbolicService()
