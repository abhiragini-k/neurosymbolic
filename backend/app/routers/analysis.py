from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from app.core.database import db
from bson import ObjectId

# ... (Previous imports assumed available via existing file) ...
# I will append this to the existing file using the APPEND/replace logic is risky if I don't see the file.
# I should have added it before.
# I will use multi_replace or simply overwrite analysis.py with the FULL content including standard imports I used before + WS.
# Actually I'll use multi_replace to add the import and the endpoint.
# But I don't see the file content right now in my thought process (I know what I wrote).
# I'll just append it or rewrite the file. Rewriting is safer to ensure order.

from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, WebSocket, WebSocketDisconnect
from app.core.database import get_database, db as database_instance 
# Note: db from database.py is the instance wrapper, get_database returns the client[db_name]
from app.models.user import User
from app.models.job import Job, JobCreate, JobStatus
from app.core.security import get_current_user
from app.services.analysis_workflow import process_analysis_job
from bson import ObjectId
import asyncio

router = APIRouter()

@router.post("/submit", response_model=Job, summary="Submit analysis job", description="Submits an entity name (e.g., a drug or disease) for neurosymbolic repurposing analysis. Initiates a background job and returns the Job model with `PENDING` status. The ID from this response is used to track progress.")
async def submit_analysis(
    job_in: JobCreate, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db=Depends(get_database)
):
    # Create Job
    job = Job(
        user_id=str(current_user.id),
        input_text=job_in.input_text,
        status=JobStatus.PENDING
    )
    
    job_data = job.dict(by_alias=True, exclude={"id"})
    if "_id" in job_data and job_data["_id"] is None:
        del job_data["_id"]
    
    new_job = await db["jobs"].insert_one(job_data)
    created_job = await db["jobs"].find_one({"_id": new_job.inserted_id})
    job_model = Job(**created_job)
    
    # Trigger Background Workflow
    background_tasks.add_task(process_analysis_job, job_model.id, job_model.input_text)
    
    return job_model

@router.get("/{job_id}", response_model=Job, summary="Get job status", description="Retrieves the current status and results of a specific analysis job. Returns 404 if not found or 403 if the job doesn't belong to the user.")
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_database)
):
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID")
        
    job = await db["jobs"].find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job["user_id"] != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this job")
        
    return Job(**job)

@router.get("/user", response_model=List[Job], summary="List user jobs", description="Retrieves a list of all analysis jobs submitted by the currently authenticated user, sorted by newest first.")
async def get_user_jobs(
    current_user: User = Depends(get_current_user),
    db=Depends(get_database)
):
    jobs_cursor = db["jobs"].find({"user_id": str(current_user.id)}).sort("created_at", -1)
    jobs = await jobs_cursor.to_list(length=100)
    return [Job(**job) for job in jobs]

@router.websocket("/ws/{job_id}")
async def websocket_job_status(websocket: WebSocket, job_id: str):
    await websocket.accept()
    if not ObjectId.is_valid(job_id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        # Simple Polling Mechanism for updates
        last_status = None
        while True:
            job = await database_instance.get_db()["jobs"].find_one({"_id": ObjectId(job_id)})
            if job:
                current_status = job.get("status")
                if current_status != last_status:
                    await websocket.send_json({
                        "job_id": job_id,
                        "status": current_status,
                        "result": job.get("result")
                    })
                    last_status = current_status
                
                if current_status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                    break
            else:
                 await websocket.send_json({"error": "Job not found"})
                 break
                 
            await asyncio.sleep(1) # Poll every second
            
    except WebSocketDisconnect:
        print(f"Client disconnected from job {job_id}")
