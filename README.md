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

Performance testing is done using Locust:

```bash
# Install Locust
pip install locust

# Run tests
cd locust
locust -f locustfile.py
```

## License

MIT
