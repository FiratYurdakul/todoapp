# To-Do Cloud App Architecture

This document outlines the architecture of the To-Do Cloud Application with MongoDB Authentication.

## Architecture Overview

```
                                                                           
                     ┌─────────────────────────────────────────────────┐   
                     │             Google Cloud Platform               │   
                     │                                                 │   
┌───────────────┐    │   ┌─────────────┐          ┌────────────────┐   │   
│               │    │   │             │          │                │   │   
│    User's     │    │   │  Frontend   │          │  Cloud Functions   │   
│    Browser    ├────┼──►│  (GKE)      │◄────────►   (Serverless)  │   │   
│               │    │   │             │          │                │   │   
└───────────────┘    │   └──────┬──────┘          └────────┬───────┘   │   
                     │          │                          │           │   
                     │          │                          │           │   
                     │          │                          │           │   
                     │          │                          │           │   
                     │          ▼                          ▼           │   
                     │   ┌─────────────┐          ┌────────────────┐   │   
                     │   │             │          │                │   │   
                     │   │  MongoDB    │◄─────────┤  User Auth     │   │   
                     │   │  VM Instance│          │  Service       │   │   
                     │   │             │          │                │   │   
                     │   └─────────────┘          └────────────────┘   │   
                     │                                                 │   
                     └─────────────────────────────────────────────────┘   
                                                                           
```

## Components

### 1. Frontend (React.js on GKE)
The frontend of the To-Do Cloud App is built using React.js and deployed on Google Kubernetes Engine (GKE). It provides a responsive user interface for:
- User authentication (signup/login)
- Task management (create, view, update, delete)

**Technology Stack:**
- React.js with TypeScript
- Material UI for components
- Deployed as containerized application on GKE

### 2. Cloud Functions (Serverless)
The application uses several serverless Cloud Functions to handle different aspects of the application:

**Authentication Functions:**
- `signup`: Handles user registration
- `login`: Authenticates users and issues JWT tokens
- `verifyToken`: Validates JWT tokens for protected routes

**Task Management Functions:**
- `validateTask`: Validates and stores task data
- `getUserTasks`: Retrieves tasks for an authenticated user

**Technology Stack:**
- Node.js runtime
- JWT for authentication
- MongoDB client for data persistence

### 3. Database (MongoDB)
MongoDB is deployed on a Compute Engine VM instance, providing document-based storage for:
- User accounts (email, password, name)
- Task data (title, description, due date, completion status)

**Collections:**
- `users`: Stores user information
- `tasks`: Stores task data with references to user IDs

## Authentication Flow

1. **Signup Process:**
   - User submits registration form
   - Frontend sends data to `signup` cloud function
   - Cloud function validates data, hashes password, and stores in MongoDB
   - JWT token is generated and returned to frontend

2. **Login Process:**
   - User submits login credentials
   - Frontend sends data to `login` cloud function
   - Cloud function verifies credentials against MongoDB
   - JWT token is returned to authenticated users

3. **Session Management:**
   - JWT token is stored in browser's localStorage
   - Token is included in Authorization header for subsequent API requests
   - `verifyToken` function validates token for protected operations

## Task Management Flow

1. **Creating Tasks:**
   - User fills task form in frontend
   - Data sent to `validateTask` function with JWT token
   - Function validates token and stores task in MongoDB

2. **Retrieving Tasks:**
   - Frontend requests user's tasks via `getUserTasks` function
   - Function validates JWT token and extracts user ID
   - Only tasks belonging to the authenticated user are returned

## Data Security

- Passwords are hashed using bcrypt before storage
- JWT secrets are stored as environment variables
- MongoDB restricts access through authentication
- All API calls require valid JWT tokens for user-specific operations

## Deployment Architecture

- Frontend is deployed as container on GKE with auto-scaling
- Cloud Functions are deployed as serverless compute
- MongoDB runs on dedicated Compute Engine VM
- All components communicate over HTTPS with JWT authentication

## Scalability Considerations

- GKE provides auto-scaling for the frontend based on load
- Cloud Functions automatically scale based on incoming requests
- MongoDB can be scaled by upgrading VM size or implementing sharding for larger deployments 