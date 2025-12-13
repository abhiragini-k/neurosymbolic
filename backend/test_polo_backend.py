import sys
import os

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(os.path.dirname(BASE_DIR), "temp")
sys.path.append(TEMP_DIR)

print(f"Testing Polo Agent from: {TEMP_DIR}")

try:
    cwd = os.getcwd()
    os.chdir(TEMP_DIR)
    from polo_sci4 import RobustPoloAgent
    agent = RobustPoloAgent()
    
    print("\n--- Running Explanation Test ---")
    drug = "Metformin"
    disease = "Type 2 diabetes mellitus"
    print(f"Input: {drug} -> {disease}")
    
    agent.explain(drug, disease)
    print("\n--- Test Complete ---")
    
except Exception as e:
    print(f"\n❌ CRASHED: {e}")
    import traceback
    traceback.print_exc()
finally:
    os.chdir(cwd)
