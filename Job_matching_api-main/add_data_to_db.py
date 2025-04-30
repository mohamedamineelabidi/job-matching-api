import os
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey, ARRAY, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import TSVECTOR, JSONB
from typing import List, Dict, Any, Tuple
from tqdm import tqdm
from openai import OpenAI
import pymupdf4llm
from groq import Groq

# Define SQLAlchemy Base
Base = declarative_base()

# Define the model for Job embeddings
class JobEmbedding(Base):
    __tablename__ = 'job_embeddings'
    
    id = Column(Integer, primary_key=True)
    job_title = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=False)
    job_summary = Column(Text)
    embedding = Column(ARRAY(Float), nullable=False)
    job_metadata = Column(JSONB, default={})
    content_vector = Column(TSVECTOR)
    
    def __repr__(self):
        return f"<JobEmbedding(id={self.id}, title={self.job_title})>"

# Create indices for faster retrieval
Index('idx_job_embedding_vector', JobEmbedding.content_vector, postgresql_using='gin')
Index('idx_job_title', JobEmbedding.job_title)

class JobEmbeddingStore:
    def __init__(self, db_uri: str = None, openai_api_key: str = None, groq_api_key: str = None):
        """Initialize the PostgreSQL job embedding store"""
        if not db_uri:
            db_uri = os.environ.get("DATABASE_URL", "postgresql+psycopg2://job_posts:j1o2b3_p4o5s6t7s8@linkedin-job-posts.postgres.database.azure.com:5432/postgres")
        
        self.engine = create_engine(db_uri)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize the embedding model
        self.openai_api_key = openai_api_key or os.environ.get("AZURE_OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("Azure OpenAI API key is required")
        self.openai_client = OpenAI(
            api_key=self.openai_api_key,
            api_version="2024-02-15-preview",
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com/"),
            azure_deployment="text-embedding-3-small",
            default_headers={"api-key": self.openai_api_key}
        )

        
        # Initialize Azure OpenAI for summarization
        self.openai_client_gpt4 = OpenAI(
            api_key=self.openai_api_key,
            api_version="2024-02-15-preview",
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com/"),
            azure_deployment="gpt-4",
            default_headers={"api-key": self.openai_api_key}
        )
    
    def store_job(self, job_title: str, job_description: str, 
                 job_summary: str = None, job_metadata: Dict[str, Any] = None):
        """
        Store a single job with its embedding in the database
        
        Args:
            job_title: Title of the job
            job_description: Full job description text
            job_summary: Optional summary of the job description
            metadata: Optional metadata dictionary (e.g., company, location, salary)
        
        Returns:
            id: The ID of the stored job
        """
        session = self.Session()
        
        try:
            # Generate embedding for the job
            job_text = f"{job_title} {job_description}"
            if job_summary:
                job_text += f" {job_summary}"
                
            response = self.openai_client.embeddings.create(
                input=job_text,
                model="text-embedding-3-small",
                deployment_id="text-embedding-3-small"
            )
            embedding = response.data[0].embedding
            
            # Create new job record
            job_embedding = JobEmbedding(
                job_title=job_title,
                job_description=job_description,
                job_summary=job_summary,
                embedding=embedding,
                job_metadata=job_metadata or {}
            )
            
            # Add to session
            session.add(job_embedding)
            
            # Update tsvector for text search
            search_text = f"{job_title} {job_description}"
            if job_summary:
                search_text += f" {job_summary}"
                
            job_embedding.content_vector = func.to_tsvector('english', search_text)
            
            # Commit changes
            session.commit()
            
            return job_embedding.id
        
        except Exception as e:
            session.rollback()
            print(f"Error storing job: {e}")
            raise
        
        finally:
            session.close()
    
    def store_batch_jobs(self, job_titles: List[str], job_descriptions: List[str], 
                        job_summaries: List[str] = None, 
                        metadata_list: List[Dict[str, Any]] = None, 
                        batch_size: int = 100):
        """
        Store a batch of jobs with their embeddings in the database
        
        Args:
            job_titles: List of job titles
            job_descriptions: List of job descriptions
            job_summaries: Optional list of job summaries
            metadata_list: Optional list of metadata dictionaries
            batch_size: Number of jobs to process at once
        """
        if job_summaries is None:
            job_summaries = [None] * len(job_titles)
        
        if metadata_list is None:
            metadata_list = [{}] * len(job_titles)
        
        # Process in smaller batches
        for i in tqdm(range(0, len(job_titles), batch_size), desc="Storing job batches"):
            session = self.Session()
            try:
                batch_records = []
                end_idx = min(i + batch_size, len(job_titles))
                
                # Generate embeddings for this batch
                batch_embeddings = []
                for j in range(i, end_idx):
                    job_text = f"{job_titles[j]} {job_descriptions[j]}"
                    if job_summaries[j]:
                        job_text += f" {job_summaries[j]}"
                        
                    response = self.openai_client.embeddings.create(
                        input=job_text,
                        model="text-embedding-3-small"
                    )
                    embedding = response.data[0].embedding
                    batch_embeddings.append(embedding)
                
                # Create job records
                for j, embedding in enumerate(batch_embeddings):
                    idx = i + j
                    job_embedding = JobEmbedding(
                        job_title=job_titles[idx],
                        job_description=job_descriptions[idx],
                        job_summary=job_summaries[idx],
                        embedding=embedding,
                        metadata=metadata_list[idx]
                    )
                    
                    # Create tsvector
                    search_text = f"{job_titles[idx]} {job_descriptions[idx]}"
                    if job_summaries[idx]:
                        search_text += f" {job_summaries[idx]}"
                        
                    job_embedding.content_vector = func.to_tsvector('english', search_text)
                    
                    batch_records.append(job_embedding)
                
                # Add all records
                session.bulk_save_objects(batch_records)
                
                # Commit
                session.commit()
                
            except Exception as e:
                session.rollback()
                print(f"Error in batch {i//batch_size}: {e}")
            finally:
                session.close()
    
    def summarize_job_text(self, content, prompt=None):
        """
        Summarize job text using Azure OpenAI GPT-4.
        """
        if prompt is None:
            prompt="""

                You are a highly intelligent assistant tasked with analyzing CVs and creating concise, structured summaries optimized for comparing with job descriptions.

                Your goal is to extract and organize key details into specific categories. Structure your response as follows:

                1. **Professional Summary**: Provide a Five-sentences max overview of the candidate’s career focus, expertise, and achievements.
                2. **Key Skills and Expertise**: Enumerate the candidate's main skills, including technical skills (e.g., programming languages, tools,frameworks, services) and non-technical skills (e.g., leadership, communication).
                3. **Work Experience**:
                - For each role, include:
                    - Job Title.
                    - Organization Name.
                    - Duration of Employment.
                    - Key responsibilities and accomplishments.
                4. **Technologies and Tools**: List every software, programming languages, frameworks,API service, and tools the candidate has experience with.
                5. **Education**: Summarize degrees, fields of study, and institutions attended.
                6. **Certifications and Training**: Highlight any certifications, courses, or training programs completed.
                7. **Languages**: Mention languages the candidate knows and their proficiency levels.
                8. **Projects**: Include significant projects or achievements relevant to the candidate's profile.
                9. **Keywords**: Extract important keywords that characterize the candidate’s expertise.

                Focus on clarity and precision in each section to ensure a well-structured summary. Here's the CV content:

                {content}

                Respond in the requested structured format.

                """
            
        chat_completion = self.openai_client_gpt4.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "you are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt.format(content=content),
                }
            ],
            model="gpt-4",
            deployment_id="gpt-4",
            temperature=0,
            max_tokens=2048,
            top_p=1,
        )
        return chat_completion.choices[0].message.content
    
    def find_matching_jobs_for_cv(self, cv_path: str, k: int = 5, generate_cv_summary: bool = True,
                                prompt_cv: str = None) -> List[Tuple[Dict, float]]:
        """
        Find jobs matching a CV by generating CV embedding and comparing to job embeddings
        
        Args:
            cv_path: Path to the CV PDF file
            k: Number of matching jobs to return
            generate_cv_summary: Whether to generate a summary for the CV
            prompt_cv: Custom prompt for CV summarization
            
        Returns:
            List of tuples containing (job_info, similarity_score)
        """
        # Extract text from CV
        cv_markdown = pymupdf4llm.to_markdown(cv_path, page_chunks=True)
        cv_text = " ".join([chunk['text'] for chunk in cv_markdown])
        
        # Generate CV summary if requested
        cv_summary = None
        if generate_cv_summary:
            if prompt_cv is None:
                prompt_cv = """
                Please analyze the following CV/resume and create a concise summary 
                highlighting the person's skills, experience, and qualifications. Focus on 
                key technical skills, years of experience, major accomplishments, and 
                education. This will be used for job matching.
                
                {content}
                """
            cv_summary = self.summarize_job_text(cv_text, prompt_cv)
        
        # Generate embedding for CV
        cv_query = cv_summary if cv_summary else cv_text
        return self.find_matching_jobs(cv_query, k)
    
    def find_matching_jobs(self, query_text: str, k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Find jobs matching a query text by generating query embedding and comparing to job embeddings
        
        Args:
            query_text: Query text (can be CV text, CV summary, or any text)
            k: Number of matching jobs to return
            
        Returns:
            List of tuples containing (job_info, similarity_score)
        """
        session = self.Session()
        try:
            # Generate embedding for query using OpenAI
            response = self.openai_client.embeddings.create(
                input=query_text,
                model="text-embedding-3-small",
                deployment_id="text-embedding-3-small"
            )
            query_embedding = response.data[0].embedding
            
            # First, filter candidates using tsvector for efficiency
            search_query = func.plainto_tsquery('english', query_text)
            
            # This query uses the GIN index on tsvector for fast filtering
            candidates = session.query(JobEmbedding).filter(
                JobEmbedding.content_vector.op('@@')(search_query)
            ).order_by(
                func.ts_rank(JobEmbedding.content_vector, search_query).desc()
            ).limit(min(k * 20, 1000)).all()
            
            if not candidates or len(candidates) < k:
                print("Not enough matching records found with tsvector. Using broader search.")
                # Fallback to a broader search if needed - get random jobs up to a limit
                existing_ids = [c.id for c in candidates]
                additional_candidates = session.query(JobEmbedding).filter(
                    ~JobEmbedding.id.in_(existing_ids)
                ).order_by(func.random()).limit(1000 - len(candidates)).all()
                
                candidates.extend(additional_candidates)
            
            # Calculate cosine similarity with candidates
            results = []
            for job in candidates:
                # Regenerate embedding for job using the same model as query
                job_text = f"{job.job_title} {job.job_description}"
                if job.job_summary:
                    job_text += f" {job.job_summary}"
                
                job_response = self.openai_client.embeddings.create(
                    input=job_text,
                    model="text-embedding-3-small",
                    deployment_id="text-embedding-3-small"
                )
                job_embedding = job_response.data[0].embedding
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, job_embedding)
                
                # Create job info dictionary
                job_info = {
                    "id": job.id,
                    "job_title": job.job_title,
                    "job_description": job.job_description,
                    "job_summary": job.job_summary,
                    "metadata": job.metadata
                }
                
                results.append((job_info, float(similarity)))
            
            # Sort by similarity score and take top k
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:k]
        
        except Exception as e:
            print(f"Error during job matching: {e}")
            return []
        finally:
            session.close()
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        
        # Avoid division by zero
        if norm_a == 0 or norm_b == 0:
            return 0
        
        return dot_product / (norm_a * norm_b)
    
    def get_job_by_id(self, job_id: int) -> Dict:
        """Retrieve a specific job by ID"""
        session = self.Session()
        try:
            job = session.query(JobEmbedding).filter(JobEmbedding.id == job_id).first()
            if job:
                return {
                    "id": job.id,
                    "job_title": job.job_title,
                    "job_description": job.job_description,
                    "job_summary": job.job_summary,
                    "metadata": job.metadata
                }
            return None
        finally:
            session.close()
    
    def search_jobs_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict]:
        """Search jobs by keyword using tsvector"""
        session = self.Session()
        try:
            search_query = func.plainto_tsquery('english', keyword)
            jobs = session.query(JobEmbedding).filter(
                JobEmbedding.content_vector.op('@@')(search_query)
            ).order_by(
                func.ts_rank(JobEmbedding.content_vector, search_query).desc()
            ).limit(limit).all()
            
            return [{
                "id": job.id,
                "job_title": job.job_title,
                "job_summary": job.job_summary,
                "metadata": job.metadata
            } for job in jobs]
        finally:
            session.close()

# Example usage
def main():
    # Initialize the job embedding store, these should be in env or config file
    job_store = JobEmbeddingStore(
        db_uri="postgresql+psycopg2://job_posts:j1o2b3_p4o5s6t7s8@linkedin-job-posts.postgres.database.azure.com:5432/postgres",
        jina_api_key="jina_71a2d1c8cf884d6593a35a6a5d89ad2fp2BEEYkIHuIpXMXv7PIXHfFOk5vU",
        groq_api_key="gsk_...."
    )
    
    # Example: Match a CV to jobs in the database
    matching_jobs = job_store.find_matching_jobs_for_cv(
        cv_path="/content/Ismail-Oubah-EnglishCV.pdf",
        k=3
    )
    
    # Display matching jobs
    print("Top matching jobs for your CV:")
    for job, score in matching_jobs:
        print(f"Match score: {score:.4f}")
        print(f"Title: {job['job_title']}")
        print(f"Summary: {job['job_summary'][:150]}..." if job['job_summary'] else "No summary")
        print("-" * 60)

if __name__ == '__main__':
    # Initialize the store
    store = JobEmbeddingStore()
    
    # Add some test job data
    test_jobs = [
        {
            'title': 'Senior Software Engineer',
            'description': 'Looking for an experienced software engineer with Python, FastAPI, and machine learning expertise. Must have experience with cloud services and team leadership.',
            'summary': 'Senior developer role focusing on Python backend development and ML.',
            'metadata': {'company': 'Tech Corp', 'location': 'Remote', 'salary': '120k-150k'}
        },
        {
            'title': 'Machine Learning Engineer', 
            'description': 'Seeking ML engineer with strong Python skills and experience in building recommendation systems. Knowledge of cloud platforms required.',
            'summary': 'ML engineering role focused on recommendation systems.',
            'metadata': {'company': 'AI Solutions', 'location': 'New York', 'salary': '130k-160k'}
        }
    ]
    
    # Store the test jobs
    for job in test_jobs:
        store.store_job(
            job_title=job['title'],
            job_description=job['description'],
            job_summary=job['summary'],
            job_metadata=job['metadata']
        )
    
    print('Test jobs added successfully!')