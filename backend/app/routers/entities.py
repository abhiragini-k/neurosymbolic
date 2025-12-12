from fastapi import APIRouter, HTTPException, Query
from app.services.mapping_service import mapping_service
from typing import Optional, Dict

router = APIRouter()

@router.get("/resolve", summary="Resolve entity name", description="Resolves a text query (e.g., 'Metformin') to a canonical Node ID in the Knowledge Graph. Use this before submitting an analysis to ensure the entity exists.")
async def resolve_entity(text: str = Query(..., description="Entity name to resolve")):
    entity_id = mapping_service.resolve_text(text)
    if not entity_id:
        return {"found": False, "query": text}
    
    node_id = mapping_service.get_node_id(entity_id)
    info = mapping_service.get_entity_info(node_id)
    
    return {
        "found": True,
        "query": text,
        "entity_id": entity_id,
        "node_id": node_id,
        "details": info
    }
