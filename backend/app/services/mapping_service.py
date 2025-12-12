import pandas as pd
import os
from typing import Dict, Any, Optional
from app.core.config import settings

class MappingService:
    _instance = None
    
    def __init__(self):
        self.text_to_entity_id: Dict[str, str] = {}
        self.entity_id_to_node_id: Dict[str, int] = {}
        self.node_id_to_entity_info: Dict[int, Dict[str, Any]] = {}
        self.alias_to_canonical: Dict[str, str] = {}
        self.initialized = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MappingService()
        return cls._instance

    def load_mappings(self):
        if self.initialized:
            return

        nodes_path = os.path.join(settings.KG_DATA_DIR, "nodes.csv")
        if not os.path.exists(nodes_path):
            print(f"WARNING: Mapping file not found at {nodes_path}")
            return

        # Load CSV
        # Expected columns: neo4j_id, label, name, identifier, new_id (model index)
        # Note: 'new_id' is assumed to be the model-ready integer ID based on build scripts.
        try:
            df = pd.read_csv(nodes_path)
            
            # Ensure required columns exist
            required_cols = ['name', 'identifier']
            if not all(col in df.columns for col in required_cols):
                 print(f"ERROR: nodes.csv missing required columns. Found: {df.columns}")
                 # Fallback if new_id is missing, maybe rely on index? 
                 # But request requires specific mapping.
                 # Let's hope new_id exists or we create it.
            
            has_new_id = 'new_id' in df.columns
            
            for index, row in df.iterrows():
                name = str(row['name']).strip() if pd.notna(row['name']) else ""
                identifier = str(row['identifier']).strip()
                label = row['label']
                
                # Determine node_id
                node_id = int(row['new_id']) if has_new_id else index
                
                # 1. Text to Entity ID
                if name:
                    self.text_to_entity_id[name.lower()] = identifier
                
                # 2. Entity ID to Node ID
                self.entity_id_to_node_id[identifier] = node_id
                
                # 3. Node ID to Entity Info
                self.node_id_to_entity_info[node_id] = {
                    "entity_id": identifier,
                    "name": name,
                    "type": label
                }
                
                # 4. Alias mapping (Naive implementation: name is canonical)
                if name:
                    self.alias_to_canonical[name.lower()] = name

            print(f"Loaded {len(df)} entity mappings.")
            self.initialized = True
            
        except Exception as e:
            print(f"Error loading mappings: {e}")

    def resolve_text(self, text: str) -> Optional[str]:
        """Returns entity_id (identifier) for input text."""
        return self.text_to_entity_id.get(text.lower())

    def get_node_id(self, entity_id: str) -> Optional[int]:
        """Returns model node_id for an entity_id."""
        return self.entity_id_to_node_id.get(entity_id)

    def get_entity_info(self, node_id: int) -> Optional[Dict[str, Any]]:
        """Returns entity info for a model node_id."""
        return self.node_id_to_entity_info.get(node_id)

mapping_service = MappingService.get_instance()
