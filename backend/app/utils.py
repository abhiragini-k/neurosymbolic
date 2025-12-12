import json
import os
from typing import Dict, Any, Optional

# Constants for file paths (relative to backend root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPOUND_MAPPING_PATH = os.path.join(BASE_DIR, "compound_id_to_name.json")
DISEASE_MAPPING_PATH = os.path.join(BASE_DIR, "disease_id_to_name.json")

_compound_id_to_name: Dict[str, str] = {}
_compound_name_to_id: Dict[str, str] = {}
_disease_id_to_name: Dict[str, str] = {}
_disease_name_to_id: Dict[str, str] = {}

def load_json(path: str) -> Dict[str, Any]:
    """Load a JSON file from the given path."""
    if not os.path.exists(path):
        print(f"Warning: File not found: {path}")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_mappings():
    """Load all necessary mappings into memory."""
    global _compound_id_to_name, _compound_name_to_id
    global _disease_id_to_name, _disease_name_to_id
    
    _compound_id_to_name = load_json(COMPOUND_MAPPING_PATH)
    _disease_id_to_name = load_json(DISEASE_MAPPING_PATH)
    
    # Create reverse mappings
    _compound_name_to_id = {v.lower().strip(): k for k, v in _compound_id_to_name.items()}
    _disease_name_to_id = {v.lower().strip(): k for k, v in _disease_id_to_name.items()}

    print(f"Loaded {len(_compound_id_to_name)} drugs and {len(_disease_id_to_name)} diseases.")

def drug_name_to_id(name: str) -> Optional[str]:
    """Convert drug name to ID."""
    if not _compound_id_to_name:
        load_mappings()
    return _compound_name_to_id.get(name.lower().strip())

def disease_name_to_id(name: str) -> Optional[str]:
    """Convert disease name to ID."""
    if not _disease_id_to_name:
        load_mappings()
    return _disease_name_to_id.get(name.lower().strip())

def disease_id_to_name(id_str: str) -> Optional[str]:
    """Convert disease ID to name."""
    if not _disease_id_to_name:
        load_mappings()
    return _disease_id_to_name.get(str(id_str))

def drug_id_to_name(id_str: str) -> Optional[str]:
    """Convert drug ID to name."""
    if not _compound_id_to_name:
        load_mappings()
    return _compound_id_to_name.get(str(id_str))
