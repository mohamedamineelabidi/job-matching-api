from sqlalchemy import Column, Integer, String, Float, Text, ARRAY, Index, ForeignKey
from sqlalchemy.dialects.postgresql import TSVECTOR, JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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
        return f"<JobEmbedding(id={self.id}, title={self.job_title})"

# Create indices for faster retrieval
Index('idx_job_embedding_vector', JobEmbedding.content_vector, postgresql_using='gin')
Index('idx_job_title', JobEmbedding.job_title)