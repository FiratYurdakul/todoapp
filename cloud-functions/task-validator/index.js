const functions = require('@google-cloud/functions-framework');
const { v4: uuidv4 } = require('uuid');

/**
 * HTTP Cloud Function to validate and format task data
 * 
 * @param {Object} req The request object
 * @param {Object} res The response object
 */
functions.http('validateTask', (req, res) => {
  // Set CORS headers for all responses
  res.set('Access-Control-Allow-Origin', '*');
  
  // Handle OPTIONS requests (preflight)
  if (req.method === 'OPTIONS') {
    res.set('Access-Control-Allow-Methods', 'POST');
    res.set('Access-Control-Allow-Headers', 'Content-Type');
    res.set('Access-Control-Max-Age', '3600');
    res.status(204).send('');
    return;
  }
  
  // Only allow POST requests
  if (req.method !== 'POST') {
    res.status(405).send({ error: 'Method not allowed' });
    return;
  }
  
  try {
    const taskData = req.body;
    
    // Basic validation
    if (!taskData.title || taskData.title.trim() === '') {
      return res.status(400).json({ error: 'Task title is required' });
    }
    
    // Format and validate the task
    const validatedTask = {
      id: `task_${uuidv4()}`,
      title: formatTitle(taskData.title),
      description: taskData.description ? taskData.description.trim() : '',
      completed: taskData.completed || false,
      createdAt: new Date().toISOString(),
      dueDate: taskData.dueDate,
    };
    
    // Check if due date is valid
    if (taskData.dueDate) {
      const dueDate = new Date(taskData.dueDate);
      if (isNaN(dueDate.getTime())) {
        return res.status(400).json({ error: 'Invalid due date format' });
      }
    }
    
    res.status(200).json(validatedTask);
    
  } catch (error) {
    console.error('Error validating task:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * Format the title: capitalize first letter, trim whitespace
 */
function formatTitle(title) {
  if (!title) return '';
  
  const trimmed = title.trim();
  // Capitalize the first letter of each sentence
  return trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
} 