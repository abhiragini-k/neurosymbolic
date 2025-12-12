from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId

class JobStatus(str):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisResult(BaseModel):
    # This structure mirrors the combined output of R-GCN and Neurosymbolic
    input_entity: Dict[str, Any]
    predictions: List[Dict[str, Any]] # Top K predictions
    explanations: Optional[Dict[str, Any]] = None # Neurosymbolic paths/confidence
    metadata: Optional[Dict[str, Any]] = None

class JobBase(BaseModel):
    input_text: str

class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    user_id: str
    status: str = JobStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    result: Optional[AnalysisResult] = None
    error: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}
