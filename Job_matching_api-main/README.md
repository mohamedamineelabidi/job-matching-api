# Job Matching API

## Overview

The Job Matching API is a sophisticated service that leverages AI to match CVs with job postings. It uses semantic similarity through embeddings and PostgreSQL full-text search to provide accurate job recommendations based on a candidate's resume and preferences.

## Architecture

The application follows a modern microservices architecture with the following components:

- **FastAPI Backend**: RESTful API endpoints for CV processing and job matching
- **PostgreSQL Database**: Stores job listings with vector embeddings for semantic search
- **AI Services**: Uses Jina AI for embeddings and Azure OpenAI/Groq for CV analysis
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
  - Jina AI Embeddings for semantic similarity
  - Azure OpenAI GPT-4 for CV analysis
  - Groq LLM for job summarization
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

### Azure Web App for Containers Deployment

This guide outlines deploying the Job Matching API to Azure Web App for Containers using the Azure CLI.

**Prerequisites:**

- Azure CLI installed and configured
- Docker installed locally
- Access to Azure subscription
- An Azure Container Registry (ACR) with the application's Docker image pushed.

**Steps:**

1.  **Log in to Azure:**
    ```bash
    az login
    ```

2.  **Set your default subscription (if you have multiple):**
    ```bash
    az account set --subscription "Your Subscription Name or ID"
    ```

3.  **Create a Resource Group (if you don't have one):**
    ```bash
    az group create --name job-matching-api-rg --location eastus
    ```
    Replace `eastus` with your desired Azure region.

4.  **Create an Azure App Service Plan (if you don't have one):**
    ```bash
    az appservice plan create --name job-matching-api-plan --resource-group job-matching-api-rg --sku B1 --is-linux
    ```
    This creates a basic Linux App Service Plan. Adjust the `--sku` as needed for your workload.

5.  **Create an Azure Web App for Containers:**
    ```bash
    az webapp create --resource-group job-matching-api-rg --plan job-matching-api-plan --name job-matching-api-app --deployment-container-image-name jobmatchingapijobmatchingapirg.azurecr.io/job-matching-api:latest
    ```
    Replace `jobmatchingapijobmatchingapirg.azurecr.io/job-matching-api:latest` with the actual name and tag of your Docker image in ACR.

6.  **Configure Application Settings (Environment Variables):**
    You need to configure the environment variables required by the application (e.g., `DATABASE_URL`, `AZURE_OPENAI_API_KEY`). It's recommended to store sensitive information in Azure Key Vault and reference it in your Web App settings.

    ```bash
    az webapp config appsettings set --name job-matching-api-app --resource-group job-matching-api-rg --settings DATABASE_URL="your_database_url" AZURE_OPENAI_API_KEY="your_azure_openai_api_key" AZURE_OPENAI_ENDPOINT="your_azure_openai_endpoint" AZURE_OPENAI_GPT4_DEPLOYMENT="your_gpt4_deployment_name" AZURE_OPENAI_EMBEDDING_DEPLOYMENT="your_embedding_deployment_name" AZURE_OPENAI_API_VERSION="your_api_version"
    ```
    Replace the placeholder values with your actual environment variable values. For production, consider using Key Vault references: `@Microsoft.KeyVault(SecretUri=https://<your-key-vault-name>.vault.azure.net/secrets/<your-secret-name>/<your-secret-version>)`.

7.  **Access the Application:**
    Once the deployment is complete, you can access your Web App at `https://job-matching-api-app.azurewebsites.net/`. The API documentation should be available at `https://job-matching-api-app.azurewebsites.net/docs`.

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
