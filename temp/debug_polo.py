import sys
import os
sys.path.append(os.getcwd())
import polo_sci4

print("Starting debug...")
try:
    agent = polo_sci4.TargetedAgent()
    print("Agent initialized.")
    # Metformin ID: 869 (from previous steps)
    # Type 2 Diabetes ID: 1
    drug_id = "869"
    disease_id = "1"
    print(f"Explaining {drug_id} -> {disease_id}")
    agent.explain(drug_id, disease_id)
    print("Explain finished.")
    
    if os.path.exists("viz_data.json"):
        print("viz_data.json created.")
        with open("viz_data.json", "r") as f:
            print(f"Content length: {len(f.read())}")
    else:
        print("viz_data.json NOT created.")
        
except Exception as e:
    print(f"Error: {e}")
