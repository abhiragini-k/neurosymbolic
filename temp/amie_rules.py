import os
import subprocess
import csv
from neo4j import GraphDatabase

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"

AMIE_JAR_PATH = "C:/Users/kabhi/Downloads/amie3.5.1.jar"   # Path to your downloaded AMIE jar
DATA_EXPORT_FILE = "graph_dump.tsv"
RULES_OUTPUT_FILE = "mined_rules.txt"

# --- OPTIMIZATION SETTINGS FOR "MORE RULES" ---
# Lowering these thresholds increases the number of rules found.
MIN_SUPPORT = 2           # Keep at 2 (The absolute minimum possible)
MIN_CONFIDENCE = 0.01     # LOWER THIS: From 0.1 (10%) -> 0.01 (1%). Accepts very rare patterns.
MIN_PCA_CONFIDENCE = 0.01 # LOWER THIS: Accepts rules that are rarely true but valid.
MAX_RULE_LENGTH = 4       # INCREASE THIS: From 3 -> 4. Finds longer, complex chains.
                          # Warning: This makes mining much slower but finds WAY more rules
def export_neo4j_to_tsv():
    """
    Fetches all relationships from Neo4j and saves them as Subject <tab> Predicate <tab> Object.
    """
    print(f"[1/3] Connecting to Neo4j at {NEO4J_URI}...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    query = """
    MATCH (s)-[r]->(o)
    // Optional: Filter for specific labels to make rules more relevant
    // WHERE (s:Compound OR s:Gene OR s:Disease) AND (o:Compound OR o:Gene OR o:Disease)
    RETURN s.id AS subject, type(r) AS predicate, o.id AS object
    """
    
    print("      Exporting triples (this may take a moment for large graphs)...")
    with driver.session() as session:
        result = session.run(query)
        
        with open(DATA_EXPORT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            count = 0
            for record in result:
                # AMIE requires: Subject <TAB> Predicate <TAB> Object
                # Ensure IDs are strings and have no internal tabs
                s = str(record['subject']).strip()
                p = str(record['predicate']).strip()
                o = str(record['object']).strip()
                writer.writerow([s, p, o])
                count += 1
                
    driver.close()
    print(f"      ✅ Exported {count} triples to {DATA_EXPORT_FILE}")

def run_amie_mining():
    """
    Runs the AMIE Jar via subprocess with optimized flags.
    """
    print(f"[2/3] Running AMIE Rule Mining...")
    
    if not os.path.exists(AMIE_JAR_PATH):
        print(f"❌ Error: AMIE Jar not found at {AMIE_JAR_PATH}")
        print("   Please download it from https://github.com/lajus/amie/releases")
        return

    # Build command
    # java -jar amie.jar -mins 2 -minc 0.1 -minpca 0.1 -maxad 3 data.tsv
    cmd = [
        "java", "-jar", AMIE_JAR_PATH,
        "-mins", str(MIN_SUPPORT),
        "-minc", str(MIN_CONFIDENCE),
        "-minpca", str(MIN_PCA_CONFIDENCE),
        "-maxad", str(MAX_RULE_LENGTH),
        # "-datalog",  # Optional: Outputs convenient format (Head <= Body)
        DATA_EXPORT_FILE
    ]
    
    print(f"      Executing: {' '.join(cmd)}")
    
    # Run and capture output
    with open(RULES_OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        # AMIE prints rules to Stdout, so we redirect to file
        process = subprocess.run(cmd, stdout=outfile, stderr=subprocess.PIPE, text=True)
        
    if process.returncode != 0:
        print(f"❌ AMIE Failed: {process.stderr}")
    else:
        print(f"      ✅ Rules mined and saved to {RULES_OUTPUT_FILE}")

def parse_and_display_rules():
    """
    Reads the raw AMIE output and displays the top rules.
    """
    print(f"[3/3] Parsing Rules...")
    
    rules = []
    if not os.path.exists(RULES_OUTPUT_FILE):
        return

    with open(RULES_OUTPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Parse AMIE output lines (skip headers/empty)
            # Typical line: Rule [Confidence] [PCA Conf] [Support] ...
            if "=>" in line:
                rules.append(line)

    print(f"\n✨ Extracted {len(rules)} Rules. Top 10 by default sort:")
    for r in rules[:10]:
        print(f"   {r}")
        
    print(f"\n(Check {RULES_OUTPUT_FILE} for full list)")

if __name__ == "__main__":
    # 1. Get Data
    export_neo4j_to_tsv()
    
    # 2. Mine Rules
    run_amie_mining()
    
    # 3. Show Results
    parse_and_display_rules()