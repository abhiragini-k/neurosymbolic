
import pickle
import os
import sys

# Add temp to path for polo import if needed
sys.path.append(os.path.join(os.getcwd(), "temp"))

path = "c:/Users/kabhi/neurosymbolic/finalKG/data/graph_index.pkl"

def check_ids():
    drug_id = "869"
    disease_id = "1"
    
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
            
            print(f"Graph loaded. Type: {type(data)}")
            
            # Check Drug
            if drug_id in data:
                print(f"✅ Drug ID {drug_id} FOUND in graph.")
                print(f"   Neighbors: {len(data[drug_id])}")
            else:
                print(f"❌ Drug ID {drug_id} NOT found in graph.")
                
            # Check Disease
            if disease_id in data:
                print(f"✅ Disease ID {disease_id} FOUND in graph.")
                print(f"   Neighbors: {len(data[disease_id])}")
            else:
                 print(f"❌ Disease ID {disease_id} NOT found in graph.")
                 
            # Try to run polo logic directly
            try:
                import polo_sci4
                agent = polo_sci4.TargetedAgent()
                print("Running polo explain...")
                paths = agent.explain(drug_id, disease_id)
                print(f"Polo found {len(paths)} paths.")
                if paths:
                    print(f"Top path: {paths[0]}")
            except Exception as e:
                print(f"Error running polo dry run: {e}")

        except Exception as e:
            print(f"Error loading pickle: {e}")
    else:
        print("File not found.")

if __name__ == "__main__":
    check_ids()
