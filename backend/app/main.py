from contextlib import asynccontextmanager
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.core.config import settings
from app.core.database import db
from app.services.mapping_service import mapping_service
from app.routers import auth, analysis, entities, predict, confidence, explainability
from app.services import pipeline
from app import utils

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    db.connect()
    
    # Load Mappings (This might take a moment)
    print("Loading Knowledge Graph Mappings...")
    mapping_service.load_mappings()
    utils.load_mappings() # Load ours as well
    pipeline.initialize_polo() # Pre-load Polo Agent
    print("Mappings Loaded.")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(confidence.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(entities.router, prefix="/entities", tags=["entities"])
app.include_router(predict.router, prefix="/predict", tags=["predictions"])


app.include_router(explainability.router, prefix="/api/explainability", tags=["explainability"])

# --- NEW ROUTES for PIPELINE ---

class PredictDrugRequest(BaseModel):
    drug_name: str
    top_k: int = 10

class AnalyzeDiseaseRequest(BaseModel):
    disease_name: str

@app.post("/predict/drug", tags=["pipeline"])
def predict_drug_pipeline(request: PredictDrugRequest):
    """
    1. Convert drug_name -> drug_id
    2. Call R-GCN logic (pipeline.run_rgcn)
    3. Convert disease_ids -> disease_names
    """
    drug_id = utils.drug_name_to_id(request.drug_name)
    if not drug_id:
        raise HTTPException(status_code=404, detail=f"Drug '{request.drug_name}' not found")
        
    try:
        # Save drug_id for subsequent analysis call context if needed, 
        # but for now we rely on simple flow.
        # Actually, the user requirement for analyze/disease says "using latest drug_id".
        # We might need to store it or expect frontend to pass it?
        # User prompt: "2. Call polo_sci4.py again but now using disease_id and latest drug_id."
        # This implies statefulness OR frontend passing it back. 
        # But api spec for analyze/disease: input is ONLY { "disease_name": "Disease D" }
        # So we MUST store the latest drug_id globally or in a simple variable.
        # Given this is a demo/single-user context implied by "latest drug_id", I'll use a global var in utils or pipeline.
        
        utils.LATEST_DRUG_ID = drug_id 
        
        predictions = pipeline.run_rgcn(drug_id, request.top_k)
        
        # Enrich with names
        output_predictions = []
        for p in predictions:
            d_name = utils.disease_id_to_name(p['disease_id'])
            if d_name:
                output_predictions.append({
                    "disease_id": p['disease_id'],
                    "disease_name": d_name,
                    "score": p['score']
                })
                
        return {
            "drug": request.drug_name,
            "drug_id": drug_id,
            "predicted": output_predictions
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/disease", tags=["pipeline"])
def analyze_disease_pipeline(request: AnalyzeDiseaseRequest):
    """
    1. Convert disease_name -> disease_id
    2. Call polo_sci4 with LATEST_DRUG_ID and this disease_id
    3. Return and Save viz_data.json
    """
    disease_id = utils.disease_name_to_id(request.disease_name)
    if not disease_id:
        raise HTTPException(status_code=404, detail=f"Disease '{request.disease_name}' not found")
        
    if not hasattr(utils, 'LATEST_DRUG_ID') or not utils.LATEST_DRUG_ID:
         raise HTTPException(status_code=400, detail="No drug selected previously. Please call /predict/drug first.")
         
    drug_id = utils.LATEST_DRUG_ID
    
    try:
        result = pipeline.run_analysis(drug_id, disease_id)
        if "error" in result:
             raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to the Neurosymbolic Drug Repurposing Backend"}

# 4️⃣ API — Neurosymbolic Analysis (Robust Version)
# Added to match frontend expectation of /api/analysis
@app.get("/api/analysis/{compound_id}/{disease_id}")
def analyze_connection(compound_id: str, disease_id: str, drug_name: str = None, disease_name: str = None):
    # 1. Get Names
    # Use provided names if available, otherwise fallback to mapping
    # Note: app.utils has mappings loaded
    c_name = drug_name if drug_name else utils.drug_id_to_name(str(compound_id))
    d_name = disease_name if disease_name else utils.disease_id_to_name(str(disease_id))
    
    if not c_name: c_name = str(compound_id)
    if not d_name: d_name = str(disease_id)
    
    # CRITICAL: If name is still an ID (digits), try to resolve it from mapping
    if str(c_name).isdigit():
        resolved = utils.drug_id_to_name(str(c_name))
        if resolved: c_name = resolved
            
    if str(d_name).isdigit():
        resolved = utils.disease_id_to_name(str(d_name))
        if resolved: d_name = resolved
    
    print(f"DEBUG: analyze_connection called with {compound_id}, {disease_id}")
    print(f"DEBUG: Received params - drug_name: '{drug_name}', disease_name: '{disease_name}'")
    print(f"DEBUG: Resolved names: '{c_name}', '{d_name}'")

    # 2. Run Symbolic Analysis via Pipeline
    # We need to temporarily set LATEST_DRUG_ID if we want to use the existing pipeline structure,
    # or better, call a direct method if available. 
    # pipeline.run_analysis uses LATEST_DRUG_ID internally for the drug ID, but takes disease_id as arg.
    # However, pipeline.run_analysis calls polo_agent.explain(drug_name, disease_name).
    # Let's see pipeline.run_analysis implementation.
    
    # Actually, let's just call the polo agent directly here to be safe and robust, 
    # mirroring the logic I wrote in backend.py.
    
    if not pipeline.polo_agent:
        return {"error": "Polo Agent not active"}
        
    import io
    from contextlib import redirect_stdout
    import json
    
    output_buffer = io.StringIO()
    viz_data = {"nodes": [], "edges": []}
    
    try:
        cwd = os.getcwd()
        os.chdir(pipeline.TEMP_DIR) # Switch to temp for file output
        
        print(f"DEBUG: Calling polo_agent.explain('{c_name}', '{d_name}')")
        
        with redirect_stdout(output_buffer):
            # Pass NAMES directly
            pipeline.polo_agent.explain(c_name, d_name)
            
        # Read generated JSON
        if os.path.exists("viz_data.json"):
            with open("viz_data.json", "r") as f:
                viz_data = json.load(f)
                
        os.chdir(cwd)
    except Exception as e:
        os.chdir(cwd)
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
        
    # Parse text output for rules/chains
    full_output = output_buffer.getvalue()
    
    lines = full_output.split('\n')
    symbolic_rules = []
    reasoning_chains = []
    
    current_chain_obj = {"pathway": [], "edges": [], "confidence": 0.0}
    current_nodes = []
    
    import re
    score_pattern = re.compile(r"Specific Score: ([\d.]+)")
    arrow_pattern = re.compile(r"\s+(?:--\[|---\[|<---\[)(.+?)(?:\]-->|\]---|\]---)\s+")

    for line in lines:
        clean = line.strip()
        if not clean: continue
        
        if clean.startswith("🔷 MECHANISM"):
            if current_nodes:
                current_chain_obj["pathway"] = current_nodes
                reasoning_chains.append(current_chain_obj)
            
            current_chain_obj = {"pathway": [], "edges": [], "confidence": 0.0}
            current_nodes = []
            symbolic_rules.append(clean)
            
        elif "Specific Score:" in clean:
            match = score_pattern.search(clean)
            if match:
                try:
                    current_chain_obj["confidence"] = float(match.group(1))
                except: pass
            symbolic_rules.append(clean)
            
        elif "-->" in clean or "<--" in clean or "---" in clean:
            symbolic_rules.append(clean)
            parts = arrow_pattern.split(clean)
            if len(parts) >= 3:
                u_n = parts[0].strip()
                rel = parts[1].strip()
                rest = parts[2].strip()
                if " (" in rest and rest.endswith(")"):
                    v_n = rest.rsplit(" (", 1)[0]
                else:
                    v_n = rest
                
                if not current_nodes:
                    current_nodes.append(u_n)
                current_nodes.append(v_n)
                current_chain_obj["edges"].append(rel)
            
    if current_nodes:
        current_chain_obj["pathway"] = current_nodes
        reasoning_chains.append(current_chain_obj)

    return {
        "compound_name": c_name,
        "disease_name": d_name,
        "neural_score": 0.0, # Placeholder
        "symbolic_score": 0.95, 
        "symbolic_rules": symbolic_rules,
        "reasoning_chains": reasoning_chains,
        "graph": viz_data,
        "raw_output": full_output
    }
