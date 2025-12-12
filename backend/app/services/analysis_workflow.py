from datetime import datetime
from app.core.database import db
from app.models.job import Job, JobStatus, AnalysisResult
from app.services.mapping_service import mapping_service
from app.services.model_service import model_service
import logging

logger = logging.getLogger(__name__)

async def process_analysis_job(job_id: str, input_text: str):
    """
    Orchestrates the full analysis workflow.
    """
    try:
        # 1. Update status to processing
        await db.client[db.get_db().name]["jobs"].update_one(
            {"_id": job_id}, 
            {"$set": {"status": JobStatus.PROCESSING}}
        )

        # 2. Entity Resolution
        # Try exact match or alias
        entity_id = mapping_service.resolve_text(input_text)
        
        if not entity_id:
            raise ValueError(f"Entity '{input_text}' not found in Knowledge Graph.")
            
        source_node_id = mapping_service.get_node_id(entity_id)
        if source_node_id is None:
             raise ValueError(f"Internal Error: Node ID not found for entity {entity_id}")

        source_info = mapping_service.get_entity_info(source_node_id)

        # 3. Model Inference (R-GCN)
        predictions_raw = await model_service.predict_rgcn(source_node_id)
        
        # 4. Human-Readable Conversion & Neurosymbolic Reasoning
        processed_predictions = []
        
        for pred in predictions_raw:
            target_node_id = pred['node_id']
            score = pred['score']
            
            target_info = mapping_service.get_entity_info(target_node_id)
            target_name = target_info['name'] if target_info else f"Unknown_Node_{target_node_id}"
            
            # Neurosymbolic Explanation
            explanation = await model_service.get_neurosymbolic_explanation(
                source_node_id, 
                target_node_id
            )
            
            processed_predictions.append({
                "target_name": target_name,
                "target_id": target_info['entity_id'] if target_info else None,
                "score": score,
                "type": target_info['type'] if target_info else pred.get('type'),
                "explanation": explanation
            })

        # 5. Store Results
        result = AnalysisResult(
            input_entity=source_info,
            predictions=processed_predictions,
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
        
        await db.client[db.get_db().name]["jobs"].update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": JobStatus.COMPLETED,
                    "result": result.dict()
                }
            }
        )

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        await db.client[db.get_db().name]["jobs"].update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": JobStatus.FAILED,
                    "error": str(e)
                }
            }
        )
