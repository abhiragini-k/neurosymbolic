from fastapi import APIRouter, HTTPException, Query
from app.services import pipeline
from app import utils

router = APIRouter()

@router.get("/confidence-breakdown")
def get_confidence_breakdown(
    drug_id: str = Query(..., description="ID or Name of the drug"),
    disease_id: str = Query(..., description="ID or Name of the disease")
):
    """
    Get a detailed confidence breakdown for a specific drug-disease pair.
    """
    try:
        # Resolve IDs if names are provided
        final_drug_id = drug_id
        if not drug_id.isdigit():
            # Try to resolve name
            resolved = utils.drug_name_to_id(drug_id)
            if not resolved:
                 raise HTTPException(status_code=404, detail=f"Drug '{drug_id}' not found")
            final_drug_id = resolved
            
        final_disease_id = disease_id
        if not disease_id.isdigit():
             # Try to resolve name
             resolved = utils.disease_name_to_id(disease_id)
             if not resolved:
                  raise HTTPException(status_code=404, detail=f"Disease '{disease_id}' not found")
             final_disease_id = resolved

        # Check if pipeline has loaded data (it lazy loads, but good to ensure)
        result = pipeline.get_confidence_breakdown(final_drug_id, final_disease_id)
        
        if not result:
             raise HTTPException(status_code=404, detail="Could not generate confidence breakdown")
             
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

