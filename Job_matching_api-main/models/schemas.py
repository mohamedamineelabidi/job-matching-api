from pydantic import BaseModel, Field
from typing import Optional, List, Any # Removed Dict import

# Simplified JobBase to match JobPosting fields more closely
class JobBase(BaseModel):
    job_title: Optional[str] = None # Made optional as it might not always be present
    job_description: Optional[str] = None # Made optional
    company: Optional[str] = None
    location: Optional[str] = None
    level: Optional[str] = None
    # Removed job_summary and metadata as they are not in the new table

class JobCreate(JobBase):
    # Add other required fields for creation if necessary
    pass

class JobResponse(JobBase):
    id: str # Changed from int to str to match JobPosting.id (Text)
    match_score: Optional[float] = None # Keep for potential future scoring logic

    # Add other fields from JobPosting that should be in the response
    description: Optional[str] = None
    key_responsibilities: Optional[str] = None
    required_qualifications: Optional[str] = None
    preferred_qualifications: Optional[str] = None
    benefits: Optional[str] = None
    salary: Optional[str] = None
    application_instructions: Optional[str] = None

    class Config:
        from_attributes = True

class CVMatchResponse(BaseModel):
    matches: List[JobResponse]
    summary: Optional[str] = None

class JobSearchResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
