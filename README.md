# Todo Cloud Application

A cloud-native To-Do List application deployed on Google Cloud Platform. This project demonstrates the implementation of a cloud-native architecture using three key components:

1. **Frontend**: React application containerized and deployed on Google Kubernetes Engine (GKE)
2. **Serverless Function**: Task validation using Google Cloud Functions
3. **Database**: MongoDB running on Google Compute Engine VM

## Architecture

```
┌─────────────┐     ┌───────────────┐     ┌───────────────┐
│   Frontend  │────▶│ Task Validator│────▶│  MongoDB VM   │
│   (GKE)     │◀────│(Cloud Function)│◀────│(Compute Engine)│
└─────────────┘     └───────────────┘     └───────────────┘
       ▲
       │
       ▼
┌─────────────┐
│    Users    │
└─────────────┘
```

## Features

- Create, read, update, and delete tasks
- Task validation using serverless function
- Persistent storage in MongoDB
- Responsive UI with Material UI
- Cloud-native deployment with Kubernetes

## Technology Stack

- **Frontend**: React, TypeScript, Material UI
- **Serverless**: Google Cloud Functions (Node.js)
- **Database**: MongoDB
- **Infrastructure**: Google Kubernetes Engine, Google Compute Engine
- **Containerization**: Docker

## Development

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm start

# Start mock API server
npm run server
```

### Deployment

The application can be deployed to Google Cloud Platform using the provided scripts:

```bash
# Deploy without Terraform (recommended)
./deploy-no-terraform.sh YOUR_PROJECT_ID

# Deploy with Terraform
./deploy.sh YOUR_PROJECT_ID
```

## Project Structure

- `/src` - React frontend code
- `/cloud-functions` - Google Cloud Functions code
- `/k8s` - Kubernetes deployment files
- `/terraform` - Infrastructure as Code (Terraform)
- `/vm-setup` - VM configuration scripts

## Performance Testing

The application includes two comprehensive performance testing approaches to evaluate scalability and stability:
Test Case 1: Frontend Kubernetes Scalability Testing
Heavy bash script load testing to evaluate HPA (Horizontal Pod Autoscaler) scaling behavior:

# Monitor HPA scaling in a separate terminal
```
kubectl get hpa todo-frontend-hpa --watch
```
Test Case 2: Locust Load Testing for Stability
Comprehensive user workflow simulation to test server stability:
bash# Install Locust
```
pip install locust
```
# Run stability test
```
locust -f kubernetes_load_test.py --headless -u 500 -r 10 -t 5m \
  --host=http://35.239.33.10 \
  --html=locust_report.html \
  --csv=results
```

## License

MIT
