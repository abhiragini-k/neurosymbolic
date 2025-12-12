from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.core.config import settings
from app.core.database import db
from app.services.mapping_service import mapping_service
from app.routers import auth, analysis, entities, predict
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
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
app.include_router(entities.router, prefix="/entities", tags=["entities"])
app.include_router(predict.router, prefix="/predict", tags=["predictions"])

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
