import axios from 'axios';
import { Task } from '../types/Task';

// This URL would be replaced with the actual Cloud Function URL when deployed
const API_URL = process.env.REACT_APP_TASK_API_URL || 'http://localhost:8080';

console.log('Task API URL:', API_URL);
console.log('Environment:', process.env.NODE_ENV);

export const validateTask = async (task: Omit<Task, 'id' | 'createdAt'>): Promise<Task> => {
  try {
    // Always call the Cloud Function in production (deployed environment)
    const response = await axios.post(`${API_URL}/api/validate-task`, task);
    console.log('Cloud Function response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error validating task:', error);
    
    // Fallback to local simulation if API call fails
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