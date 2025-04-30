# Job Matching API

## Overview

The Job Matching API is a sophisticated service that leverages AI to match CVs with job postings. It uses semantic similarity through embeddings and PostgreSQL full-text search to provide accurate job recommendations based on a candidate's resume and preferences.

## Project Structure

After reorganization, the project is structured as follows:

```
project-root/
│
├── Job_matching_api-main/
│   ├── app.py
│   ├── database/
│   ├── models/
│   ├── services/
│   ├── requirements.txt
│   └── ... (other code and resources)
│
├── .env
├── Dockerfile
├── azure-deploy.yaml
├── README.md
└── ... (other deployment/config files)
```

- **All application code, scripts, and resources are inside `Job_matching_api-main/`.**
- **The root directory contains only deployment, configuration, and environment files.**

## Architecture

The application follows a modern microservices architecture with the following components:

- **FastAPI Backend**: RESTful API endpoints for CV processing and job matching
- **PostgreSQL Database**: Stores job listings with vector embeddings for semantic search
- **AI Services**: Uses Azure OpenAI for CV analysis and embeddings
- **Docker Containerization**: Enables consistent deployment across environments
- **Azure Web App for Containers**: Manages container deployment and scaling on Azure

## Features

- **CV-Job Matching**: Uses semantic similarity to match CVs with relevant job postings
- **Full-text Job Search**: Enables keyword-based job search with PostgreSQL full-text capabilities
- **CV Processing and Analysis**: Extracts structured information from CVs using AI
- **RESTful API**: Well-documented endpoints for integration with frontend applications
- **Containerized Deployment**: Docker configuration for cloud deployment
- **Scalable Architecture**: Designed to handle large volumes of job listings and CV processing

## Technology Stack

- **Backend**: FastAPI, Python 3.11
- **Database**: PostgreSQL with vector search capabilities
- **ORM**: SQLAlchemy
- **AI/ML**:
  - Azure OpenAI GPT-4 for CV analysis and semantic similarity
- **PDF Processing**: PyMuPDF
- **Containerization**: Docker with multi-stage builds
- **Cloud Deployment**: Azure Web App for Containers

## Prerequisites

- Python 3.11+
- PostgreSQL database
- Docker and Docker Compose (for containerized development)
- Azure CLI installed and configured
- Access to Azure subscription
- API keys for:
  - Azure OpenAI

## Installation and Setup

### Local Development

1. Clone the repository

2. Set up environment variables in a `.env` file at the project root:
```env
# Database Configuration
DATABASE_URL=postgresql+psycopg2://username:password@host:5432/dbname

# API Keys
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

3. Install dependencies:
```bash
pip install -r Job_matching_api-main/requirements.txt
```

4. Start the FastAPI server:
```bash
python Job_matching_api-main/app.py
```
or (for development with auto-reload):
```bash
uvicorn Job_matching_api-main.app:app --host 0.0.0.0 --port 8001 --reload
```

5. Access the API documentation at: [http://localhost:8001/docs](http://localhost:8001/docs)

### Docker Setup

1. Build the Docker image:
```bash
docker build -t job-matching-api .
```

2. Run the container:
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=your_database_url \
  -e AZURE_OPENAI_API_KEY=your_azure_openai_key \
  -e AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint \
  job-matching-api
```

## API Documentation

### Endpoints

#### POST /api/match-cv
Match a CV with jobs in the database.

- **Request**: Multipart form data
  - `cv_file`: CV file (PDF or Markdown)
  - `interests`: Optional interests
  - `soft_skills`: Optional soft skills
- **Response**: List of matching jobs with similarity scores

#### GET /api/jobs/{job_id}
Get details of a specific job.

- **Parameters**:
  - `job_id`: Job ID
- **Response**: Job details

#### GET /api/jobs/search
Search jobs by keyword.

- **Parameters**:
  - `keyword`: Search term
  - `limit`: Maximum number of results (default: 10)
- **Response**: List of matching jobs

## Deployment

### Azure Web App for Containers Deployment

The application is ready to be deployed to Azure Web App for Containers. Please refer to the Azure documentation for detailed deployment instructions.

## Security Considerations

- Store API keys and sensitive data in environment variables or secure vaults
- Use Azure Key Vault for production deployments
- The Docker image uses a non-root user for improved security
- Implement authentication and rate limiting for production use
- Use secure database connections with SSL

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[MIT License](LICENSE)

---

**Note:**
This project has been reorganized for clarity and maintainability. All application code and scripts are now inside the `Job_matching_api-main/` directory. The root directory contains only deployment, configuration, and environment files.
