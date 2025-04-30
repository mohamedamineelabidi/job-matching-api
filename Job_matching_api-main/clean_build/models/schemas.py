from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any

class JobBase(BaseModel):
    job_title: str
    job_description: str
    job_summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    match_score: Optional[float] = None

    class Config:
        from_attributes = True

class CVMatchResponse(BaseModel):
    matches: List[JobResponse]
    summary: Optional[str] = None

class JobSearchResponse(BaseModel):
    jobs: List[JobResponse]
    total: int