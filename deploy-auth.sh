#!/bin/bash
set -e

# This script deploys the MongoDB authentication components to GCP

# Check for required tools
command -v gcloud >/dev/null 2>&1 || { echo "gcloud is required but not installed. Aborting."; exit 1; }

# Variables - edit these to match your GCP project
PROJECT_ID=${1:-"todo-cloud-app-20250521"}
REGION=${2:-"us-central1"}
ZONE=${3:-"us-central1-a"}

echo "Deploying authentication components to GCP project: $PROJECT_ID in $REGION"

# Ensure we're authenticated and set the right project
gcloud auth login
gcloud config set project $PROJECT_ID

# 1. Deploy the Authentication Cloud Functions
echo "Deploying the authentication Cloud Functions..."

# Deploy signup function
cd "$(dirname "$0")/cloud-functions/auth-service"
echo "Deploying signup function..."
gcloud functions deploy signup \
  --gen2 \
  --runtime=nodejs18 \
  --region=$REGION \
  --source=. \
  --entry-point=signup \
  --trigger-http \
  --allow-unauthenticated

# Deploy login function
echo "Deploying login function..."
gcloud functions deploy login \
  --gen2 \
  --runtime=nodejs18 \
  --region=$REGION \
  --source=. \
  --entry-point=login \
  --trigger-http \
  --allow-unauthenticated

# Deploy verifyToken function
echo "Deploying verifyToken function..."
gcloud functions deploy verifyToken \
  --gen2 \
  --runtime=nodejs18 \
  --region=$REGION \
  --source=. \
  --entry-point=verifyToken \
  --trigger-http \
  --allow-unauthenticated

# 2. Update the Task Validator Cloud Function
echo "Updating the Task Validator Cloud Function..."
cd ../task-validator
gcloud functions deploy validateTask \
  --gen2 \
  --runtime=nodejs18 \
  --region=$REGION \
  --source=. \
  --entry-point=validateTask \
  --trigger-http \
  --allow-unauthenticated

# Deploy getUserTasks function
echo "Deploying getUserTasks function..."
gcloud functions deploy getUserTasks \
  --gen2 \
  --runtime=nodejs18 \
  --region=$REGION \
  --source=. \
  --entry-point=getUserTasks \
  --trigger-http \
  --allow-unauthenticated

# 3. Get MongoDB VM IP
VM_IP=$(gcloud compute instances describe mongodb-instance --zone=$ZONE --format="get(networkInterfaces[0].accessConfigs[0].natIP)")
echo "MongoDB VM IP: $VM_IP"

# 4. Set environment variables for functions
echo "Setting environment variables for Cloud Functions..."

# Set MongoDB URI and JWT Secret for auth-service functions
for FUNCTION in "signup" "login" "verifyToken"; do
  gcloud functions deploy $FUNCTION \
    --gen2 \
    --update-env-vars "MONGO_URI=mongodb://$VM_IP:27017,JWT_SECRET=your-super-secret-key-for-production" \
    --region=$REGION
done

# Set MongoDB URI and JWT Secret for task-validator functions
for FUNCTION in "validateTask" "getUserTasks"; do
  gcloud functions deploy $FUNCTION \
    --gen2 \
    --update-env-vars "MONGO_URI=mongodb://$VM_IP:27017,JWT_SECRET=your-super-secret-key-for-production" \
    --region=$REGION
done

# 5. Build and deploy the frontend with authentication
cd ../../
echo "Building and deploying the frontend with authentication..."

# Build and push the frontend container
docker build -t gcr.io/$PROJECT_ID/todo-frontend:latest .
docker push gcr.io/$PROJECT_ID/todo-frontend:latest

# Deploy to Kubernetes
kubectl apply -f k8s/frontend-deployment.yaml

echo "================================================="
echo "MongoDB Authentication Deployment Complete!"
echo "================================================="
echo "You can now use the application with user authentication."
echo "Create an account, log in, and your tasks will be stored in MongoDB."
echo "=================================================" 