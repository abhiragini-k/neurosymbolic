import sys
import os
import json

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(os.path.dirname(BASE_DIR), "temp")
sys.path.append(TEMP_DIR)

print(f"TEMP_DIR: {TEMP_DIR}")

# Mock Polo Agent loading to inspect nodes.csv directly if agent fails
# But let's try to load the agent first
try:
    os.chdir(TEMP_DIR)
    from polo_sci4 import TargetedAgent
    polo_agent = TargetedAgent()
    print("Polo Agent loaded.")
    
    name_to_polo_id = {}
    for nid, info in polo_agent.nodes.items():
        name_to_polo_id[info['name'].lower()] = nid
        
    print(f"Mapping size: {len(name_to_polo_id)}")
    
    # Check specific keys
    keys_to_check = ["caffeine", "alzheimer's disease", "cbln1", "a1bg", "0", "1", "26"]
    for k in keys_to_check:
        val = name_to_polo_id.get(k)
        print(f"Key: '{k}' -> Value: '{val}'")
        
    # Check what maps to "869" and "1"
    for k, v in name_to_polo_id.items():
        if v == "869":
            print(f"Reverse check: '{k}' maps to '869'")
        if v == "1":
            print(f"Reverse check: '{k}' maps to '1'")
            
except Exception as e:
    print(f"Failed to load agent: {e}")
    import traceback
    traceback.print_exc()
