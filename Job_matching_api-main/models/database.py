from sqlalchemy import Column, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class JobPosting(Base):
    __tablename__ = 'job_postings_jobposting'

    # Define columns based on the provided structure
    id = Column(Text, primary_key=True)  # Assuming 'id' is the primary key
    company = Column(Text)
    job_title = Column(Text)
    level = Column(Text)
    description = Column(Text)
    location = Column(Text)
    structured_content = Column(Text)
    job_description = Column(Text)
    key_responsibilities = Column(Text)
    required_qualifications = Column(Text)
    preferred_qualifications = Column(Text)
    benefits = Column(Text)
    salary = Column(Text)
    application_instructions = Column(Text)

    def __repr__(self):
        return f"<JobPosting(id={self.id}, title={self.job_title}, company={self.company})>"

# Note: Removed previous indices related to the old JobEmbedding model.
# New indices can be added here if needed for performance based on query patterns.
