#!/bin/bash
set -e

# To-Do Cloud App Deployment Script
# This script deploys the complete To-Do Cloud Application with MongoDB authentication

# Check for required tools
command -v gcloud >/dev/null 2>&1 || { echo "gcloud is required but not installed. Aborting."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "docker is required but not installed. Aborting."; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "kubectl is required but not installed. Aborting."; exit 1; }

# Set your project ID, region, and zone
PROJECT_ID=${1:-"your-gcp-project-id"}
REGION=${2:-"us-central1"}
ZONE=${3:-"us-central1-a"}

echo "======================================================================================"
echo "Deploying To-Do Cloud App to Google Cloud Platform"
echo "Project: $PROJECT_ID | Region: $REGION | Zone: $ZONE"
echo "======================================================================================"

# Ensure we're authenticated and set the right project
echo "Setting up Google Cloud project..."
gcloud auth login
gcloud config set project $PROJECT_ID

# -----------------------------------------------
# 1. Deploy MongoDB VM
# -----------------------------------------------
echo -e "\n[1/4] Deploying MongoDB Virtual Machine..."
cd "$(dirname "$0")/vm-setup"
chmod +x mongodb-startup.sh

# Create VM with startup script
echo "Creating MongoDB instance..."
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
echo "Creating firewall rule for MongoDB..."
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

# Wait for MongoDB to initialize
echo "Waiting for MongoDB to initialize (30 seconds)..."
sleep 30

# -----------------------------------------------
# 2. Deploy Authentication Cloud Functions
# -----------------------------------------------
echo -e "\n[2/4] Deploying Authentication Cloud Functions..."
cd "../cloud-functions/auth-service"

# Deploy signup function
echo "Deploying signup function..."
gcloud functions deploy signup \
  --gen2 \
  --runtime=nodejs18 \
  --region=$REGION \
  --source=. \
  --entry-point=signup \
  --trigger-http \
  --allow-unauthenticated \
  --update-env-vars "MONGO_URI=mongodb://$VM_IP:27017,JWT_SECRET=your-super-secret-key-for-production"

# Deploy login function
echo "Deploying login function..."
gcloud functions deploy login \
  --gen2 \
  --runtime=nodejs18 \
  --region=$REGION \
  --source=. \
  --entry-point=login \
  --trigger-http \
  --allow-unauthenticated \
  --update-env-vars "MONGO_URI=mongodb://$VM_IP:27017,JWT_SECRET=your-super-secret-key-for-production"

# Deploy verifyToken function
echo "Deploying verifyToken function..."
gcloud functions deploy verifyToken \
  --gen2 \
  --runtime=nodejs18 \
  --region=$REGION \
  --source=. \
  --entry-point=verifyToken \
  --trigger-http \
  --allow-unauthenticated \
  --update-env-vars "MONGO_URI=mongodb://$VM_IP:27017,JWT_SECRET=your-super-secret-key-for-production"

# -----------------------------------------------
# 3. Deploy Task Validator Cloud Functions
# -----------------------------------------------
echo -e "\n[3/4] Deploying Task Validator Cloud Functions..."
cd "../task-validator"

# Deploy validateTask function
echo "Deploying validateTask function..."
gcloud functions deploy validateTask \
  --gen2 \
  --runtime=nodejs18 \
  --region=$REGION \
  --source=. \
  --entry-point=validateTask \
  --trigger-http \
  --allow-unauthenticated \
  --update-env-vars "MONGO_URI=mongodb://$VM_IP:27017,JWT_SECRET=your-super-secret-key-for-production"

# Deploy getUserTasks function
echo "Deploying getUserTasks function..."
gcloud functions deploy getUserTasks \
  --gen2 \
  --runtime=nodejs18 \
  --region=$REGION \
  --source=. \
  --entry-point=getUserTasks \
  --trigger-http \
  --allow-unauthenticated \
  --update-env-vars "MONGO_URI=mongodb://$VM_IP:27017,JWT_SECRET=your-super-secret-key-for-production"

# -----------------------------------------------
# 4. Deploy Frontend to GKE
# -----------------------------------------------
echo -e "\n[4/4] Deploying Frontend to Google Kubernetes Engine..."
cd "../.."

# Build and push the frontend container
echo "Building and pushing the frontend container..."
docker build --platform linux/amd64 -t gcr.io/$PROJECT_ID/todo-frontend:latest .
docker push gcr.io/$PROJECT_ID/todo-frontend:latest

# Setup GKE cluster if it doesn't exist
echo "Setting up GKE cluster..."
gcloud container clusters create-auto todo-cluster \
  --region=$REGION \
  --project=$PROJECT_ID 2>/dev/null || echo "Cluster already exists, continuing..."

# Get GKE credentials
gcloud container clusters get-credentials todo-cluster \
  --region=$REGION \
  --project=$PROJECT_ID

# Deploy to Kubernetes
echo "Deploying to Kubernetes..."
cd k8s
sed -i -e "s|us-central1-docker.pkg.dev/.*/todo-frontend:latest|gcr.io/$PROJECT_ID/todo-frontend:latest|g" frontend-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# Get the external IP of the frontend service
echo "Waiting for LoadBalancer IP..."
while true; do
  EXTERNAL_IP=$(kubectl get service todo-frontend-service -o=jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
  if [ -n "$EXTERNAL_IP" ]; then
    break
  fi
  echo "Waiting for LoadBalancer IP..."
  sleep 5
done

# -----------------------------------------------
# 5. Summary
# -----------------------------------------------
echo -e "\n======================================================================================"
echo "🎉 DEPLOYMENT COMPLETE 🎉"
echo "======================================================================================"
echo "Frontend URL: http://$EXTERNAL_IP"
echo "MongoDB VM IP: $VM_IP"
echo ""
echo "Cloud Functions:"
echo "- Signup: https://$REGION-$PROJECT_ID.cloudfunctions.net/signup"
echo "- Login: https://$REGION-$PROJECT_ID.cloudfunctions.net/login"
echo "- Verify Token: https://$REGION-$PROJECT_ID.cloudfunctions.net/verifyToken"
echo "- Validate Task: https://$REGION-$PROJECT_ID.cloudfunctions.net/validateTask"
echo "- Get User Tasks: https://$REGION-$PROJECT_ID.cloudfunctions.net/getUserTasks"
echo "======================================================================================"
echo "To access MongoDB, SSH into the VM:"
echo "  gcloud compute ssh mongodb-instance --zone=$ZONE --project=$PROJECT_ID"
echo "Then use the MongoDB shell:"
echo "  mongosh"
echo "======================================================================================" 