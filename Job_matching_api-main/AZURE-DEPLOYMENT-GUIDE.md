# Azure Deployment Guide for Job Matching API

## Prerequisites
- Azure CLI installed and configured
- Docker installed locally
- kubectl installed and configured
- Access to Azure subscription

## Step 1: Resource Group Setup
```bash
# Create a new resource group if not exists
az group create --name your-resource-group --location eastus
```

## Step 2: Azure Container Registry (ACR) Setup
```bash
# Create ACR
az acr create --resource-group your-resource-group --name jobmatchingapi --sku Basic

# Log in to ACR
az acr login --name jobmatchingapi

# Build and push Docker image
docker build -t jobmatchingapi.azurecr.io/job-matching-api:latest .
docker push jobmatchingapi.azurecr.io/job-matching-api:latest
```

## Step 3: Azure Kubernetes Service (AKS) Setup
```bash
# Create AKS cluster
az aks create \
    --resource-group your-resource-group \
    --name job-matching-cluster \
    --node-count 1 \
    --enable-addons monitoring \
    --generate-ssh-keys \
    --attach-acr jobmatchingapi

# Get AKS credentials
az aks get-credentials --resource-group your-resource-group --name job-matching-cluster
```

## Step 4: Configure Secrets
```bash
# Create Azure Key Vault
az keyvault create --name jobmatchingvault --resource-group your-resource-group --location eastus

# Store secrets in Key Vault
az keyvault secret set --vault-name jobmatchingvault --name database-url --value "your-database-url"
az keyvault secret set --vault-name jobmatchingvault --name jina-api-key --value "your-jina-api-key"
az keyvault secret set --vault-name jobmatchingvault --name groq-api-key --value "your-groq-api-key"

# Create Kubernetes secrets
kubectl create secret generic api-secrets \
    --from-literal=database-url=$(az keyvault secret show --name database-url --vault-name jobmatchingvault --query value -o tsv) \
    --from-literal=jina-api-key=$(az keyvault secret show --name jina-api-key --vault-name jobmatchingvault --query value -o tsv) \
    --from-literal=groq-api-key=$(az keyvault secret show --name groq-api-key --vault-name jobmatchingvault --query value -o tsv)

# Create ACR pull secret
kubectl create secret docker-registry acr-secret \
    --docker-server=jobmatchingapi.azurecr.io \
    --docker-username=$(az acr credential show -n jobmatchingapi --query username -o tsv) \
    --docker-password=$(az acr credential show -n jobmatchingapi --query passwords[0].value -o tsv)
```

## Step 5: Deploy Application
```bash
# Apply Kubernetes configurations
kubectl apply -f k8s-deployment.yaml
kubectl apply -f k8s-service.yaml

# Verify deployment
kubectl get pods
kubectl get services
```

## Step 6: Access the Application
```bash
# Get the external IP
kubectl get service job-matching-api
```
The API will be accessible at `http://<EXTERNAL-IP>:8000`

## Monitoring and Maintenance
```bash
# View logs
kubectl logs deployment/job-matching-api

# Scale deployment
kubectl scale deployment job-matching-api --replicas=3

# Update image
kubectl set image deployment/job-matching-api job-matching-api=jobmatchingapi.azurecr.io/job-matching-api:latest
```

## Cleanup
```bash
# Delete resources when no longer needed
az group delete --name your-resource-group --yes --no-wait
```

## Troubleshooting
- If pods are not starting, check logs: `kubectl describe pod <pod-name>`
- For service issues: `kubectl describe service job-matching-api`
- ACR access issues: Verify ACR credentials and secrets
- For scaling issues: Check resource quotas and limits