from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import db
from app.services.mapping_service import mapping_service
from app.routers import auth, analysis, entities, predict

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    db.connect()
    
    # Load Mappings (This might take a moment)
    print("Loading Knowledge Graph Mappings...")
    mapping_service.load_mappings()
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

@app.get("/")
def read_root():
    return {"message": "Welcome to the Neurosymbolic Drug Repurposing Backend"}
