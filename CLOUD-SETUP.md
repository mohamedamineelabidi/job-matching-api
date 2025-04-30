# Azure Cloud Setup and Configuration Guide

## Azure Resources Setup

### Azure Container Registry (ACR)
1. Create a new ACR:
   ```bash
   az acr create --resource-group <your-resource-group> --name <registry-name> --sku Basic
   ```
2. Log in to ACR:
   ```bash
   az acr login --name <registry-name>
   ```

### Azure Database for PostgreSQL
1. Create a new PostgreSQL server in Azure Portal
2. Configure firewall rules to allow your application's IP
3. Update the DATABASE_URL in your environment:
   ```
   DATABASE_URL=postgresql+psycopg2://<username>:<password>@<server-name>.postgres.database.azure.com:5432/postgres
   ```

## API Keys Management

### Rotating API Keys
1. **JINA API Key**:
   - Generate new key from Jina Cloud Console
   - Update the key in Azure Kubernetes secrets:
     ```bash
     kubectl create secret generic api-secrets --from-literal=jina-api-key='new-key' --dry-run=client -o yaml | kubectl apply -f -
     ```

2. **Azure OpenAI API Key**:
   - Generate new key from Azure Portal > Cognitive Services
   - Update AZURE_OPENAI_API_KEY in environment
   - Update endpoint if needed (AZURE_OPENAI_ENDPOINT)

## Environment Variables

### Local Development
Create a `.env` file with:
```plaintext
# Database Configuration
DATABASE_URL=postgresql+psycopg2://<username>:<password>@<server>.postgres.database.azure.com:5432/postgres

# API Keys
JINA_API_KEY=your_jina_api_key
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Production Deployment
1. Store secrets in Azure Key Vault:
   ```bash
   az keyvault secret set --vault-name "your-keyvault" --name "database-url" --value "your-database-url"
   ```
2. Update kubernetes secrets from Key Vault

## Deployment Updates

### Updating the Application
1. Build new Docker image:
   ```bash
   docker build -t <registry-name>.azurecr.io/job-matching-api:latest .
   ```
2. Push to ACR:
   ```bash
   docker push <registry-name>.azurecr.io/job-matching-api:latest
   ```
3. Restart deployment:
   ```bash
   kubectl rollout restart deployment job-matching-api
   ```

### Monitoring
- Monitor application logs:
  ```bash
  kubectl logs deployment/job-matching-api
  ```
- Check deployment status:
  ```bash
  kubectl get deployment job-matching-api
  ```

## Security Best Practices
1. Rotate API keys regularly (every 30-90 days)
2. Use managed identities for Azure services when possible
3. Keep environment variables in Azure Key Vault
4. Enable Azure Monitor for logging and metrics
5. Regular security audits of exposed endpoints