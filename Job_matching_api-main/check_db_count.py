import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set.")
    exit(1)

try:
    # Create SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Connect to the database
    with engine.connect() as connection:
        # Execute the count query
        result = connection.execute(text("SELECT COUNT(*) FROM job_postings_jobposting;"))
        
        # Fetch the count
        count = result.scalar_one()
        
        print(f"Total number of job postings in 'job_postings_jobposting' table: {count}")

except Exception as e:
    print(f"An error occurred while connecting to the database or executing the query: {e}")
