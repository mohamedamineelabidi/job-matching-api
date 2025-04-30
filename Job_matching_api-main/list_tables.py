import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    print("Error: DATABASE_URL environment variable not set")
else:
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)

        # Inspect the database
        inspector = inspect(engine)

        # Get table names
        table_names = inspector.get_table_names()

        # Print table names
        print("Tables in the database:")
        for table_name in table_names:
            print(table_name)

    except Exception as e:
        print(f"An error occurred: {e}")
