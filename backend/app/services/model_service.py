import asyncio
from typing import List, Dict, Any
from app.services.mapping_service import mapping_service

class ModelService:
    async def predict_rgcn(self, source_node_id: int) -> List[Dict[str, Any]]:
        """
        Stub for R-GCN model service.
        Returns top-k predictions (target_node_id, score).
        """
        # Simulation delay
        await asyncio.sleep(1)
        
        # Determine strict type if possible, for now just return some dummy IDs 
        # that hopefully exist in the mapping.
        # In a real scenario, this would call a separate Microservice or run inference.
        
        # Let's return some dummy predictions compatible with mapping_service checks
        # We'll just pick some arbitrary IDs from the mapping if possible, 
        # or just random integers.
        return [
            {"node_id": 10, "score": 0.95, "type": "Disease"},
            {"node_id": 25, "score": 0.88, "type": "Gene"},
            {"node_id": 105, "score": 0.72, "type": "Compound"}
        ]

    async def get_neurosymbolic_explanation(self, source_id: int, target_id: int) -> Dict[str, Any]:
        """
        Stub for Neurosymbolic reasoning service.
        Returns paths and confidence scores.
        """
        await asyncio.sleep(0.5)
        
        # Get names for better readability in stub output
        source_info = mapping_service.get_entity_info(source_id)
        target_info = mapping_service.get_entity_info(target_id)
        
        s_name = source_info['name'] if source_info else f"Node_{source_id}"
        t_name = target_info['name'] if target_info else f"Node_{target_id}"

        return {
            "source": s_name,
            "target": t_name,
            "neural_score": 0.95, # Should match RGCN score roughly
            "symbolic_score": 0.85,
            "reasoning_chains": [
                {
                    "pathway": [s_name, "Gene_X", "Pathway_Y", t_name],
                    "confidence": 0.9
                },
                {
                    "pathway": [s_name, "Protein_Z", t_name],
                    "confidence": 0.75
                }
            ]
        }

model_service = ModelService()
