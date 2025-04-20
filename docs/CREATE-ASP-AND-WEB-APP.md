# Azure CLI: Creating App Service Plan and Web App

## 1. Create an Azure Service Plan

Note: You don't have to create a new ASP for each project, if you already have one just skip this step.

### Step 1: Log in to Azure via Azure CLI
You must log in to Azure using the Azure CLI:
```
az login
```

### Step 2: Create a Resource Group
```
az group create --name GROUP-NAME --location LOCATION
```

Variables:
* **GROUP-NAME**: Represents the name of the resource group (must be remembered for later use).
* **LOCATION**: The Azure region where services will reside (e.g., eastus).

### Step 3: Create an App Service Plan (ASP)
```
az appservice plan create --resource-group GROUP-NAME --name ASP-NAME --is-linux
```

Variable:
* **ASP-NAME**: The name of the App Service Plan. The `--is-linux` flag specifies it's a Linux plan.

## 2. Create an Azure App Service (Web App)
```
az webapp create --name WEB-APP-SERVICE-NAME --plan ASP-NAME --resource-group GROUP-NAME --deployment-container-image-name nginx:latest
```

This command will create a Web App within the specified resource group and App Service Plan, and it will initially deploy an Nginx container image.

Variable:
* **WEB-APP-SERVICE-NAME**: This will be the name of the web application (must be globally unique across all of Azure).