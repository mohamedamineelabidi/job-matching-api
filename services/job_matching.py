from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import numpy as np
from sqlalchemy import func
from openai import AzureOpenAI
import os

from models.database import JobEmbedding
from models.schemas import JobResponse

class JobMatchingService:
    def __init__(self):
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not self.azure_api_key or not self.azure_endpoint:
            raise ValueError("Azure OpenAI API key and endpoint are required")
        self.client = AzureOpenAI(
            api_key=self.azure_api_key,
            api_version="2024-02-15-preview",
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
            return 0
        
        return dot_product / (norm_a * norm_b)

    def find_matches(
        self,
        cv_content: str,
        interests: Optional[str] = None,
        soft_skills: Optional[str] = None,
        db: Session = None,
        k: int = 10
    ) -> List[JobResponse]:
        """Find matching jobs for a CV"""
        try:
            # Generate embedding for query
            query_text = cv_content
            if interests:
                query_text += f" {interests}"
            if soft_skills:
                query_text += f" {soft_skills}"

            # Generate embedding using OpenAI
            response = self.client.embeddings.create(
                input=query_text,
                model="text-embedding-3-small"
            )
            query_embedding = response.data[0].embedding
            
            # First, filter candidates using tsvector for efficiency
            search_query = func.plainto_tsquery('english', query_text)
            
            candidates = db.query(JobEmbedding).filter(
                JobEmbedding.content_vector.op('@@')(search_query)
            ).order_by(
                func.ts_rank(JobEmbedding.content_vector, search_query).desc()
            ).limit(min(k * 20, 1000)).all()
            
            if not candidates or len(candidates) < k:
                additional_candidates = db.query(JobEmbedding).order_by(
                    func.random()
                ).limit(1000 - len(candidates)).all()
                candidates.extend(additional_candidates)
            
            # Calculate similarities and prepare responses
            results = []
            for job in candidates:
                # Regenerate job embedding using the same model as query
                job_text = f"{job.job_title} {job.job_description}"
                if job.job_summary:
                    job_text += f" {job.job_summary}"
                
                job_response = self.client.embeddings.create(
                    input=job_text,
                    model="text-embedding-3-small"
                )
                job_embedding = job_response.data[0].embedding
                
                similarity = self._cosine_similarity(query_embedding, job_embedding)
                
                results.append(JobResponse(
                    id=job.id,
                    job_title=job.job_title,
                    job_description=job.job_description,
                    job_summary=job.job_summary,
                    metadata=job.job_metadata,
                    match_score=float(similarity)
                ))
            
            # Sort by similarity score and take top k
            results.sort(key=lambda x: x.match_score, reverse=True)
            return results[:k]

        except Exception as e:
            raise Exception(f"Error finding matches: {str(e)}")

    def get_job_by_id(self, job_id: int, db: Session) -> Optional[JobResponse]:
        """Get job details by ID"""
        job = db.query(JobEmbedding).filter(JobEmbedding.id == job_id).first()
        if job:
            return JobResponse(
                id=job.id,
                job_title=job.job_title,
                job_description=job.job_description,
                job_summary=job.job_summary,
                metadata=job.job_metadata
            )
        return None

    def search_jobs_by_keyword(self, keyword: str, limit: int, db: Session) -> List[JobResponse]:
        """Search jobs by keyword"""
        search_query = func.plainto_tsquery('english', keyword)
        jobs = db.query(JobEmbedding).filter(
            JobEmbedding.content_vector.op('@@')(search_query)
        ).order_by(
            func.ts_rank(JobEmbedding.content_vector, search_query).desc()
        ).limit(limit).all()
        
        return [
            JobResponse(
                id=job.id,
                job_title=job.job_title,
                job_description=job.job_description,
                job_summary=job.job_summary,
                metadata=job.job_metadata
            ) for job in jobs
        ]