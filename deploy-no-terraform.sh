#!/bin/bash
set -e

# This script deploys the To-Do app to Google Cloud Platform without using Terraform

# Check for required tools
command -v gcloud >/dev/null 2>&1 || { echo "gcloud is required but not installed. Aborting."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "docker is required but not installed. Aborting."; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "kubectl is required but not installed. Aborting."; exit 1; }

# Variables - edit these to match your GCP project
PROJECT_ID=${1:-"your-gcp-project-id"}
REGION=${2:-"us-central1"}
ZONE=${3:-"us-central1-a"}

echo "Deploying to GCP project: $PROJECT_ID in $REGION/$ZONE"

# Ensure we're authenticated and set the right project
gcloud auth login
gcloud config set project $PROJECT_ID

# Build and push the frontend container
cd "$(dirname "$0")"
echo "Building and pushing the frontend container..."
docker build -t gcr.io/$PROJECT_ID/todo-frontend:latest .
docker push gcr.io/$PROJECT_ID/todo-frontend:latest

# Deploy the Cloud Function
echo "Deploying the task validation Cloud Function..."
cd cloud-functions/task-validator
gcloud functions deploy validateTask \
  --gen2 \
  --runtime=nodejs20 \
  --region=$REGION \
  --source=. \
  --entry-point=validateTask \
  --trigger-http \
  --allow-unauthenticated

# Get the Cloud Function URL
FUNCTION_URL=$(gcloud functions describe validateTask --gen2 --region=$REGION --format="value(serviceConfig.uri)")
echo "Cloud Function deployed at: $FUNCTION_URL"

# Create a .env file with the Cloud Function URL
cd ../../
echo "REACT_APP_TASK_API_URL=$FUNCTION_URL" > .env

# Deploy MongoDB VM using gcloud directly
echo "Deploying MongoDB VM using gcloud..."
cd vm-setup
chmod +x mongodb-startup.sh

# Create VM with startup script
gcloud compute instances create mongodb-instance \
  --project=$PROJECT_ID \
  --zone=$ZONE \
  --machine-type=e2-medium \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --metadata-from-file=startup-script=mongodb-startup.sh \
  --tags=mongodb,database \
  --scopes=storage-ro,logging-write,monitoring-write

# Create firewall rule for MongoDB
gcloud compute firewall-rules create allow-mongodb \
  --project=$PROJECT_ID \
  --direction=INGRESS \
  --priority=1000 \
  --network=default \
  --action=ALLOW \
  --rules=tcp:27017 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=mongodb

# Get the MongoDB VM IP address
VM_IP=$(gcloud compute instances describe mongodb-instance --zone=$ZONE --format="get(networkInterfaces[0].accessConfigs[0].natIP)")
echo "MongoDB VM deployed at: $VM_IP"

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to initialize (30 seconds)..."
sleep 30

# Update frontend config with MongoDB VM IP
cd ../
echo "REACT_APP_MONGODB_URL=mongodb://$VM_IP:27017/todo" >> .env

# Rebuild and push frontend with updated config
echo "Rebuilding and pushing the frontend container with updated config..."
docker build -t gcr.io/$PROJECT_ID/todo-frontend:latest .
docker push gcr.io/$PROJECT_ID/todo-frontend:latest

# Setup GKE cluster if not exists
echo "Setting up GKE cluster..."
gcloud container clusters create-auto todo-cluster \
  --region=$REGION \
  --project=$PROJECT_ID

# Get GKE credentials
gcloud container clusters get-credentials todo-cluster \
  --region=$REGION \
  --project=$PROJECT_ID

# Deploy to Kubernetes
echo "Deploying to Kubernetes..."
cd k8s
perl -i -pe "s/PROJECT_ID/$PROJECT_ID/g" frontend-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# Get the external IP of the frontend service
echo "Waiting for LoadBalancer IP..."
while true; do
  EXTERNAL_IP=$(kubectl get service todo-frontend-service -o=jsonpath='{.status.loadBalancer.ingress[0].ip}')
  if [ -n "$EXTERNAL_IP" ]; then
    break
  fi
  echo "Waiting for LoadBalancer IP..."
  sleep 5
done

echo "========================================"
echo "Deployment complete!"
echo "Frontend URL: http://$EXTERNAL_IP"
echo "Cloud Function URL: $FUNCTION_URL"
echo "MongoDB VM IP: $VM_IP"
echo "======================================== 