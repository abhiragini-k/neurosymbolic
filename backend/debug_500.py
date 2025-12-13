import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from explainability.pathway_influence import compute_pathway_influence
    from explainability.gene_match import compute_gene_match
    
    print("Testing compute_pathway_influence...")
    try:
        res = compute_pathway_influence("Metformin", "type 2 diabetes mellitus")
        print("Success:", res.keys())
    except Exception as e:
        print("Error in compute_pathway_influence:")
        import traceback
        traceback.print_exc()

    print("\nTesting compute_gene_match...")
    try:
        res = compute_gene_match("Metformin", "type 2 diabetes mellitus")
        print("Success:", res.keys())
    except Exception as e:
        print("Error in compute_gene_match:")
        import traceback
        traceback.print_exc()

    print("\nTesting pipeline.run_analysis...")
    try:
        from app.services.pipeline import run_analysis
        res = run_analysis("Metformin", "type 2 diabetes mellitus")
        if "error" in res:
            print(f"Pipeline Error: {res['error']}")
        else:
            print("Pipeline Success:", res.keys())
            if "graph" in res:
                print(f"Graph Nodes: {len(res['graph']['nodes'])}")
                print(f"Graph Edges: {len(res['graph']['edges'])}")
    except Exception as e:
        print("Error in pipeline.run_analysis:")
        import traceback
        traceback.print_exc()

except ImportError as e:
    print(f"Import Error: {e}")
    # Try to find where we are
    print(f"CWD: {os.getcwd()}")
    print(f"Path: {sys.path}")
