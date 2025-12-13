from explainability.pathway_influence import compute_pathway_influence

try:
    print("Testing Pathway Influence Aggregation (MAX)...")
    # Using the known valid drug/disease names
    result = compute_pathway_influence("Metformin", "Alzheimer's disease")
    
    pathways = result.get("pathway_influence", [])
    print(f"Pathways found: {len(pathways)}")
    
    if pathways:
        top_p = pathways[0]
        print(f"Top Pathway: {top_p['pathway']}")
        print(f"Influence Score: {top_p['influence']}")
        
        if top_p['influence'] > 0.05:
            print("SUCCESS: Score is visible!")
        else:
            print("WARNING: Score is still very low.")
    else:
        print("ERROR: No pathways returned.")
        
except Exception as e:
    print(f"CRASH: {e}")
