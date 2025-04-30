# Job Matching API

This is a FastAPI-based job matching service that provides CV processing and job matching capabilities.

## Local Development

1. Build the Docker image:
```bash
docker build -t job-matching-api .
```

2. Run the container locally:
```bash
docker run -p 8000:8000 job-matching-api
```

## Deploying to Azure

1. Create an Azure Container Registry (ACR):
```bash
az acr create --resource-group <your-resource-group> --name <registry-name> --sku Basic
```

2. Log in to ACR:
```bash
az acr login --name <registry-name>
```

3. Tag and push the image:
```bash
docker tag job-matching-api <registry-name>.azurecr.io/job-matching-api:latest
docker push <registry-name>.azurecr.io/job-matching-api:latest
```

4. Create a secret for API keys:
```bash
kubectl create secret generic api-secrets \
  --from-literal=database-url='your-database-url' \
  --from-literal=jina-api-key='your-jina-api-key' \
  --from-literal=groq-api-key='your-groq-api-key'
```

5. Deploy to Azure Container Apps:
```bash
kubectl apply -f azure-deploy.yaml
```

## API Documentation

Once deployed, you can access the API documentation at:
- Local: http://localhost:8000/docs
- Azure: https://<your-app-url>/docs

## Environment Variables

The following environment variables need to be set:
- `DATABASE_URL`: PostgreSQL connection string
- `JINA_API_KEY`: API key for Jina embeddings
- `GROQ_API_KEY`: API key for Groq LLM