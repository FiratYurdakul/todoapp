const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = process.env.PORT || 8080;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Task validation endpoint
app.post('/api/validate-task', (req, res) => {
  try {
    const taskData = req.body;
    
    // Basic validation
    if (!taskData.title || taskData.title.trim() === '') {
      return res.status(400).json({ error: 'Task title is required' });
    }
    
    // Format and validate the task
    const validatedTask = {
      id: `task_${uuidv4()}`,
      title: taskData.title.trim(),
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
    
    // Simulate some processing delay
    setTimeout(() => {
      res.status(200).json(validatedTask);
    }, 300);
    
  } catch (error) {
    console.error('Error validating task:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'OK' });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Mock server running on port ${PORT}`);
}); 