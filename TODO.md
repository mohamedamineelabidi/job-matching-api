# TODO List: Update Database Connection and Logic

1.  **Update Database Connection String:**
    *   Locate the file(s) where the database connection string is defined (likely in `database/session.py`, `models/database.py`, or a configuration file).
    *   Replace the existing connection string with the new Azure PostgreSQL connection string: `postgresql://postgres:z%K8$UgKEHzvx*p@arya-database-dev-server.postgres.database.azure.com:5432/arya_db?sslmode=require`.

2.  **Update Database Interaction Logic:**
    *   Identify the code responsible for database interactions (e.g., SQLAlchemy models in `models/database.py`, query logic in `services/job_matching.py` or `app.py`).
    *   Update the code to use the correct table name: `job_postings_jobposting`.
    *   Ensure the code correctly maps to the new table structure:
        *   `id` (text)
        *   `company` (text)
        *   `job_title` (text)
        *   `level` (text)
        *   `description` (text)
        *   `location` (text)
        *   `structured_content` (text)
        *   `job_description` (text)
        *   `key_responsibilities` (text)
        *   `required_qualifications` (text)
        *   `preferred_qualifications` (text)
        *   `benefits` (text)
        *   `salary` (text)
        *   `application_instructions` (text)

3.  **Update Dependencies:**
    *   Check `requirements.txt`.
    *   Ensure a PostgreSQL driver like `psycopg2-binary` is listed. Add it if it's missing.

4.  **Test Changes:**
    *   Run any existing tests or manually test the application's database functionality to confirm the connection and data retrieval/manipulation work as expected.
