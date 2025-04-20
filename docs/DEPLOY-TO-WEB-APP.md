# Deploying Applications on Azure Web App

## 1. Preparing a Docker Image:

You need to prepare a docker image that runs on port 80.
Here's an example Dockerfile:

```Dockerfile
# Build stage
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY . .

# Expose port
EXPOSE 80

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
```

## 2. Deployment using Github Actions:

For deployment via Github Actions, we need to:
- Create a Docker image for the application
- Publish it to the Github Container Registry
- Finally, deploy it to Azure App Services

Here's a template for the yml file that will do this manually (I'll explain manual deployment later):

```yaml
name: Deploy to Azure Web App

env:
  AZURE_WEBAPP_NAME: WEB-APP-SERVICE-NAME

on:
  workflow_dispatch: 

permissions:
  contents: 'read'
  packages: 'write'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Check out the repository
        uses: actions/checkout@v4

      - name: Set up Docker Builder
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub container registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Lowercase the repo name
        run: echo "REPO=${GITHUB_REPOSITORY,,}" >>${GITHUB_ENV}

      - name: Build and push container image to registry
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ env.REPO }}:${{ github.sha }}
          file: ./Dockerfile

  deploy:
    runs-on: ubuntu-latest

    needs: build

    steps:
      - name: Lowercase the repo name
        run: echo "REPO=${GITHUB_REPOSITORY,,}" >>${GITHUB_ENV}
        
      - name: Deploy to Azure Web App
        id: deploy-to-webapp
        uses: azure/webapps-deploy@v3
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME }}
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
          images: 'ghcr.io/${{ env.REPO }}:${{ github.sha }}'
```

### Variables:
- WEB-APP-SERVICE-NAME: Enter the name of the service you created
- AZURE_WEBAPP_PUBLISH_PROFILE: The value for this variable comes from your Web App service page and must be placed in the Repository secrets (see images below)

Note: If this repository is private, you'll need to take additional steps.

### Step 1: Add the AZURE_WEBAPP_PUBLISH_PROFILE secret to your repository settings:

![alt text](./images/Get%20Azure%20Wep%20App%20Publish%20Profile.png)

![alt text](./images/Add%20Azure%20Wep%20App%20Publish%20Profile%20to%20Repository%20secrets.png)

Then save.

### Step 2: Push the changes you've made to this repository.

For deployment, you need to do this manually (you can change this to trigger on pushes to specific branches by modifying the yml file above).

![alt text](./images/Deploy%20to%20Azure%20by%20running%20the%20workflow.png)

### Step 3: For Private repositories

If your repo is private, you need to grant Azure permission to pull the image by creating a Classic Token.

Go to your GitHub account Settings, then to Developer Settings, then to Personal access tokens,
and Generate new token (classic).

For permissions, only select read:packages, then Generate token (don't forget to give it a name).
After that, copy the Token.

Finally, you need to place it in the Deployment Center of the Web App you created.

![alt text](./images/Set%20GHRB%20access%20credentials%20in%20Azure%20Web%20App.png)