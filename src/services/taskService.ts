import axios from 'axios';
import { Task } from '../types/Task';

// Cloud Function URLs
const VALIDATE_TASK_URL = 'https://us-central1-todo-cloud-app-20250521.cloudfunctions.net/validateTask';
const GET_TASKS_URL = 'https://us-central1-todo-cloud-app-20250521.cloudfunctions.net/getUserTasks';

// Local development API URL for fallback
const LOCAL_API_URL = process.env.REACT_APP_TASK_API_URL || 'http://localhost:8080';

// Debug logging for development
if (process.env.NODE_ENV === 'development') {
  console.log('Task API URL:', LOCAL_API_URL);
  console.log('Environment:', process.env.NODE_ENV);
}

/**
 * Validates and creates a task through the Cloud Function
 */
export const validateTask = async (
  task: Omit<Task, 'id' | 'createdAt'>, 
  authToken?: string | null
): Promise<Task> => {
  try {
    // Set up headers with authentication if available
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    };

    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }

    // Call the Cloud Function
    const response = await axios.post(VALIDATE_TASK_URL, task, { headers });
    return response.data;
  } catch (error) {
    console.error('Error validating task:', error);
    
    // Fallback to local validation if API call fails
    console.log('Falling back to local validation');
    const validatedTask: Task = {
      ...task,
      id: `task_${Date.now()}`,
      title: task.title.trim(),
      description: task.description?.trim() || '',
      createdAt: new Date().toISOString(),
    };
    
    return validatedTask;
  }
};

/**
 * Fetches all tasks for the authenticated user
 */
export const fetchUserTasks = async (authToken: string): Promise<Task[]> => {
  try {
    const response = await axios.get(GET_TASKS_URL, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Error fetching user tasks:', error);
    throw error;
  }
}; 