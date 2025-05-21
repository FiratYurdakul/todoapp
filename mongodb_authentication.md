# MongoDB Authentication Integration

## Overview

This document outlines how MongoDB is used for user authentication and task management in the Todo Cloud Application.

## Implementation Components

### 1. MongoDB Setup (VM-based)
- MongoDB is deployed on a Google Compute Engine VM
- Setup script: `vm-setup/mongodb-startup.sh`
- Database name: `todo_app`
- Collections: `users` and `tasks`

### 2. Authentication Cloud Function
- Location: `cloud-functions/auth-service/`
- Endpoints:
  - `signup`: Creates new user accounts
  - `login`: Authenticates existing users
  - `verifyToken`: Validates JWT tokens

### 3. Task Management Cloud Functions
- Location: `cloud-functions/task-validator/`
- Enhanced to support user-specific tasks:
  - `validateTask`: Now supports authentication and saves tasks to MongoDB
  - `getUserTasks`: New endpoint to retrieve a user's tasks

### 4. Frontend Authentication
- New components:
  - `components/Auth.tsx`: Login/signup form
- Updated components:
  - `App.tsx`: Authentication state management
  - `taskService.ts`: Support for authenticated API calls

## Data Models

### User Schema
```javascript
{
  _id: ObjectId,
  email: String,
  password: String, // bcrypt hashed
  name: String,
  createdAt: Date,
  lastLogin: Date
}
```

### Task Schema
```javascript
{
  _id: ObjectId,
  title: String,
  description: String,
  completed: Boolean,
  createdAt: Date,
  dueDate: Date,
  userId: String // Reference to user
}
```

## Authentication Flow

1. **User Registration**:
   - User submits signup form
   - Cloud Function validates input
   - Password is hashed using bcrypt
   - User is stored in MongoDB
   - JWT token is generated and returned

2. **User Login**:
   - User submits login form
   - Cloud Function validates credentials
   - JWT token is generated and returned
   - Frontend stores token in localStorage

3. **Authenticated Actions**:
   - JWT token is included in API requests
   - Cloud Functions verify token with each request
   - Tasks are associated with the user's ID
   - User can only access their own tasks

## Security Considerations

- Passwords are hashed with bcrypt
- JWT tokens are used for stateless authentication
- MongoDB connections use secure authentication
- Tokens expire after 24 hours
- User data is validated before storage

## Testing

To test the MongoDB authentication:

1. Run the app and create a new account
2. Login with your credentials
3. Add tasks - they will be saved to your user account
4. Logout and login again - your tasks should persist

## Future Enhancements

- Add password reset functionality
- Implement role-based access control
- Add user profile management
- Enable social authentication providers 