from fastapi import APIRouter, HTTPException, Query
from explainability.pathway_influence import compute_pathway_influence
from explainability.gene_match import compute_gene_match

router = APIRouter()

@router.get("/pathway", tags=["explainability"])
def get_pathway_influence(drug_id: str = Query(..., description="The ID of the drug"), 
                          disease_id: str = Query(..., description="The ID of the disease")):
    """
    Get pathway influence scores for a drug-disease pair.
    """
    if not drug_id or not disease_id:
        raise HTTPException(status_code=400, detail="Missing drug_id or disease_id")
    
    print(f"DEBUG: Pathway Endpoint hit with drug_id='{drug_id}', disease_id='{disease_id}'")
    return compute_pathway_influence(drug_id, disease_id)

@router.get("/gene-match", tags=["explainability"])
def get_gene_match(drug_id: str = Query(..., description="The ID of the drug"), 
                   disease_id: str = Query(..., description="The ID of the disease")):
    """
    Get gene activation match scores for a drug-disease pair.
    """
    if not drug_id or not disease_id:
        raise HTTPException(status_code=400, detail="Missing drug_id or disease_id")
    
    print(f"DEBUG: GeneMatch Endpoint hit with drug_id='{drug_id}', disease_id='{disease_id}'")
    return compute_gene_match(drug_id, disease_id)
