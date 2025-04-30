from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from services.job_matching import JobMatchingService
from services.cv_processing import CVProcessingService
from database.session import get_db
from models.schemas import JobResponse, CVMatchResponse

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Job Matching API",
    description="API for CV processing and job matching",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
job_matching_service = JobMatchingService()
cv_processing_service = CVProcessingService()

class InterestsRequest(BaseModel):
    interests: str
    soft_skills: Optional[str] = None

@app.post("/api/match-cv", response_model=List[JobResponse])
async def match_cv(
    cv_file: UploadFile = File(...),
    interests: Optional[str] = None,
    soft_skills: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Match CV with jobs in the database"""
    try:
        # Process CV
        cv_content = await cv_processing_service.process_cv(cv_file)
        
        # Match with jobs
        matches = job_matching_service.find_matches(
            cv_content=cv_content,
            interests=interests,
            soft_skills=soft_skills,
            db=db
        )
        
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get job details by ID"""
    try:
        job = job_matching_service.get_job_by_id(job_id, db)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/search", response_model=List[JobResponse])
async def search_jobs(
    keyword: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Search jobs by keyword"""
    try:
        jobs = job_matching_service.search_jobs_by_keyword(keyword, limit, db)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 80))
    uvicorn.run(app, host="0.0.0.0", port=port)
