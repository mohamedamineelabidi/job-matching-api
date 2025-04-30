from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import numpy as np
import numpy as np # Added numpy import
from sqlalchemy import func
from openai import AzureOpenAI
import os
from sqlalchemy import or_ # Import or_ for keyword searching

from models.database import JobPosting # Changed JobEmbedding to JobPosting
from models.schemas import JobResponse

class JobMatchingService:
    def __init__(self):
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.embedding_deployment_name = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT") # Read deployment name
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION") # Read API version

        if not self.azure_api_key or not self.azure_endpoint:
            raise ValueError("Azure OpenAI API key and endpoint are required")
        if not self.embedding_deployment_name: # Check if deployment name is set
             raise ValueError("Azure OpenAI embedding deployment name is required (AZURE_OPENAI_EMBEDDING_DEPLOYMENT)")
        if not self.api_version: # Check if API version is set
             raise ValueError("Azure OpenAI API version is required (AZURE_OPENAI_API_VERSION)")

        self.client = AzureOpenAI(
            api_key=self.azure_api_key,
            api_version=self.api_version, # Use the API version from environment variable
            azure_endpoint=self.azure_endpoint
        )

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0 # Return float
        
        similarity = dot_product / (norm_a * norm_b)
        return similarity

    def _get_embedding(self, text: str) -> List[float]: # Removed model parameter
        """Generate embedding for the given text using Azure OpenAI."""
        if not self.embedding_deployment_name:
             # This should ideally be caught in __init__, but double-check
             raise ValueError("Embedding deployment name not configured.")
        try:
            # Use the deployment name read from environment variables
            response = self.client.embeddings.create(input=[text], model=self.embedding_deployment_name)
            return response.data[0].embedding
        except Exception as e:
            # Log the error appropriately in a real application
            # Consider more specific error handling for Azure API errors
            print(f"Error generating embedding for text snippet '{text[:50]}...': {e}")
            # Return a zero vector or handle appropriately
            # Determine dimension based on the expected model (e.g., text-embedding-3-small is 1536)
            # TODO: Make dimension dynamic or configurable if different embedding models might be used
            return [0.0] * 1536 # Assuming text-embedding-3-small dimension

    def find_matches(
        self,
        cv_content: str,
        interests: Optional[str] = None,
        soft_skills: Optional[str] = None,
        db: Session = None,
        limit: int = 10 # Renamed k to limit, default remains 10 here but will be overridden by app.py
    ) -> List[JobResponse]:
        """Find matching jobs for a CV using embedding similarity"""
        try:
            # 1. Combine input text and generate CV embedding
            query_text = cv_content
            if interests:
                query_text += f" Interests: {interests}"
            if soft_skills:
                query_text += f" Soft Skills: {soft_skills}"

            if not query_text.strip():
                 return [] # Return empty if no text provided

            cv_embedding = self._get_embedding(query_text)
            if not cv_embedding or np.linalg.norm(cv_embedding) == 0:
                 print("Warning: Could not generate a valid embedding for the CV.")
                 return [] # Cannot match without a valid CV embedding

            # 2. Retrieve candidate jobs (Consider optimizing this retrieval)
            # Option A: Retrieve all jobs (can be slow/memory intensive)
            # jobs = db.query(JobPosting).all()

            # 2. Retrieve candidate jobs
            # 2. Retrieve candidate jobs (Removed keyword pre-filtering)
            # Determine a fetch limit to get enough candidates for scoring
            fetch_limit = max(limit * 3, 100) # Fetch at least 100 or 3x the desired limit

            # Fetch jobs directly without keyword filtering.
            # Consider adding an ORDER BY clause if there's a relevant column (e.g., date_posted DESC)
            # For now, just limit the total fetched.
            jobs = db.query(JobPosting).limit(fetch_limit).all()

            if not jobs:
                print(f"No jobs found in the database (fetched up to {fetch_limit}).")
                return []
            else:
                 print(f"Fetched {len(jobs)} candidate jobs with fetch_limit={fetch_limit}.")

            # 3. Calculate scores for candidate jobs
            scored_jobs = []
            for job in jobs:
                # Combine relevant job fields into a single string for embedding
                job_text_parts = [
                    job.job_title,
                    job.description,
                    job.job_description,
                    job.key_responsibilities,
                    job.required_qualifications,
                    job.preferred_qualifications,
                    job.company # Maybe include company name?
                ]
                job_text = " ".join(filter(None, job_text_parts)) # Filter out None values

                if not job_text.strip():
                    score = 0.0 # Assign zero score if no text content for the job
                else:
                    job_embedding = self._get_embedding(job_text)
                    if not job_embedding or np.linalg.norm(job_embedding) == 0:
                        score = 0.0 # Assign zero score if embedding fails
                        print(f"Warning: Could not generate embedding for job ID {job.id}")
                    else:
                        score = self._cosine_similarity(cv_embedding, job_embedding)

                scored_jobs.append((job, score))

            # 4. Sort jobs by score (descending)
            scored_jobs.sort(key=lambda item: item[1], reverse=True)

            # 5. Format results into JobResponse
            results = [
                JobResponse(
                    id=job.id,
                    job_title=job.job_title,
                    job_description=job.job_description,
                    company=job.company,
                    location=job.location,
                    level=job.level,
                    description=job.description,
                    key_responsibilities=job.key_responsibilities,
                    required_qualifications=job.required_qualifications,
                    preferred_qualifications=job.preferred_qualifications,
                    benefits=job.benefits,
                    salary=job.salary,
                    application_instructions=job.application_instructions,
                    match_score=score # Assign calculated score
                ) for job, score in scored_jobs
            ]

            # 6. Return top 'limit' results
            return results[:limit]

        except Exception as e:
            # Log the error properly in a real application
            print(f"Error finding matches: {str(e)}")
            # Re-raise or return an empty list/error response
            raise Exception(f"Error finding matches: {str(e)}")

    def get_job_by_id(self, job_id: str, db: Session) -> Optional[JobResponse]: # Changed job_id type hint to str
        """Get job details by ID"""
        job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
        if job:
            # Updated JobResponse mapping
            return JobResponse(
                id=job.id,
                job_title=job.job_title,
                job_description=job.job_description,
                company=job.company,
                location=job.location,
                level=job.level,
                description=job.description,
                key_responsibilities=job.key_responsibilities,
                required_qualifications=job.required_qualifications,
                preferred_qualifications=job.preferred_qualifications,
                benefits=job.benefits,
                salary=job.salary,
                application_instructions=job.application_instructions,
                match_score=None # No score applicable here
            )
        return None

    def search_jobs_by_keyword(self, keyword: str, limit: int, db: Session) -> List[JobResponse]:
        """Search jobs by keyword using simple ILIKE"""
        # Remove tsvector logic, implement basic keyword search
        search_term = f"%{keyword}%"
        jobs = db.query(JobPosting).filter(
            or_(
                JobPosting.job_title.ilike(search_term),
                JobPosting.description.ilike(search_term),
                JobPosting.job_description.ilike(search_term),
                JobPosting.key_responsibilities.ilike(search_term),
                JobPosting.required_qualifications.ilike(search_term),
                JobPosting.company.ilike(search_term)
            )
        ).limit(limit).all()

        # Updated JobResponse mapping
        return [
            JobResponse(
                id=job.id,
                job_title=job.job_title,
                job_description=job.job_description,
                company=job.company,
                location=job.location,
                level=job.level,
                description=job.description,
                key_responsibilities=job.key_responsibilities,
                required_qualifications=job.required_qualifications,
                preferred_qualifications=job.preferred_qualifications,
                benefits=job.benefits,
                salary=job.salary,
                application_instructions=job.application_instructions,
                match_score=None # No score applicable here
            ) for job in jobs
        ]
