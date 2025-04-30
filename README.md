# Job Matching API

## Overview

The Job Matching API is a sophisticated service that leverages AI to match CVs with job postings. It uses semantic similarity through embeddings and PostgreSQL full-text search to provide accurate job recommendations based on a candidate's resume and preferences.

## Architecture

The application follows a modern microservices architecture with the following components:

- **FastAPI Backend**: RESTful API endpoints for CV processing and job matching
- **PostgreSQL Database**: Stores job listings with vector embeddings for semantic search
- **AI Services**: Uses Jina AI for embeddings and Azure OpenAI/Groq for CV analysis
- **Docker Containerization**: Enables consistent deployment across environments
- **Kubernetes Orchestration**: Manages container deployment, scaling, and operations

## Features

- **CV-Job Matching**: Uses semantic similarity to match CVs with relevant job postings
- **Full-text Job Search**: Enables keyword-based job search with PostgreSQL full-text capabilities
- **CV Processing and Analysis**: Extracts structured information from CVs using AI
- **RESTful API**: Well-documented endpoints for integration with frontend applications
- **Containerized Deployment**: Docker and Kubernetes configurations for cloud deployment
- **Scalable Architecture**: Designed to handle large volumes of job listings and CV processing

## Technology Stack

- **Backend**: FastAPI, Python 3.11
- **Database**: PostgreSQL with vector search capabilities
- **ORM**: SQLAlchemy
- **AI/ML**:
  - Jina AI Embeddings for semantic similarity
  - Azure OpenAI GPT-4 for CV analysis
  - Groq LLM for job summarization
- **PDF Processing**: PyMuPDF
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Kubernetes
- **Cloud Deployment**: Azure Kubernetes Service (AKS)

## Prerequisites

- Python 3.11+
- PostgreSQL database
- Docker and Docker Compose (for containerized development)
- Kubernetes CLI (kubectl) for deployment
- API keys for:
  - Jina AI
  - Azure OpenAI
  - Groq (optional, for enhanced job summarization)

## Installation and Setup

### Local Development

1. Clone the repository

2. Set up environment variables in a `.env` file:
```env
# Database Configuration
DATABASE_URL=postgresql+psycopg2://username:password@host:5432/dbname

# API Keys
JINA_API_KEY=your_jina_api_key
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
GROQ_API_KEY=your_groq_api_key

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the FastAPI server:
```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

5. Access the API documentation at: http://localhost:8000/docs

### Docker Setup

1. Build the Docker image:
```bash
docker build -t job-matching-api .
```

2. Run the container:
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=your_database_url \
  -e JINA_API_KEY=your_jina_api_key \
  -e AZURE_OPENAI_API_KEY=your_azure_openai_key \
  -e AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint \
  -e GROQ_API_KEY=your_groq_api_key \
  job-matching-api
```

## Database Setup

The application uses PostgreSQL with vector search capabilities. The database schema will be automatically created when you run the application for the first time.

### Adding Test Data

Use the provided scripts to populate the database with job listings:

```bash
# Add sample job listings
python add_data_to_db.py

# Add test jobs for development
python add_test_jobs.py
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

### Azure Deployment

Detailed instructions for deploying to Azure can be found in the [AZURE-DEPLOYMENT-GUIDE.md](AZURE-DEPLOYMENT-GUIDE.md) file. Key steps include:

1. Setting up Azure Container Registry (ACR)
2. Creating an Azure Kubernetes Service (AKS) cluster
3. Configuring secrets in Azure Key Vault
4. Deploying the application using Kubernetes manifests

```bash
# Quick deployment steps
az acr build --registry <your-acr-name> --image job-matching-api:latest .
kubectl apply -f k8s-deployment.yaml
kubectl apply -f k8s-service.yaml
```

### Kubernetes Deployment

The project includes Kubernetes manifests for deployment:

- `k8s-deployment.yaml`: Defines the deployment configuration
- `k8s-service.yaml`: Exposes the API as a service

Deploy using kubectl:

```bash
kubectl apply -f k8s-deployment.yaml
kubectl apply -f k8s-service.yaml
```

## Testing

The project includes test scripts to verify functionality:

```bash
# Test database connection
python test_db.py

# Test the API endpoints
python test_api.py
```

## Error Handling

The API includes comprehensive error handling:
- 404: Resource not found
- 500: Internal server error
- Validation errors for invalid input

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
