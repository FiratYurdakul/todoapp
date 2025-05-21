const functions = require('@google-cloud/functions-framework');
const { v4: uuidv4 } = require('uuid');
const { MongoClient, ServerApiVersion, ObjectId } = require('mongodb');
const jwt = require('jsonwebtoken');

// Configuration
const JWT_SECRET = process.env.JWT_SECRET || 'your-super-secret-key-for-development-only';
const MONGO_URI = process.env.MONGO_URI || 'mongodb://35.232.144.78:27017'; // Replace with your VM's actual IP
const DB_NAME = 'todo_app';

// MongoDB client
let client;
let db;

// Initialize MongoDB connection
async function connectToMongoDB() {
  if (client) return client;
  
  client = new MongoClient(MONGO_URI, {
    serverApi: {
      version: ServerApiVersion.v1,
      strict: true,
      deprecationErrors: true,
    }
  });
  
  try {
    await client.connect();
    console.log('Connected to MongoDB');
    db = client.db(DB_NAME);
    return client;
  } catch (err) {
    console.error('Failed to connect to MongoDB:', err);
    throw err;
  }
}

// Verify JWT token
function verifyToken(token) {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    console.error('Token verification failed:', error.message);
    return null;
  }
}

/**
 * HTTP Cloud Function to validate and format task data
 * 
 * @param {Object} req The request object
 * @param {Object} res The response object
 */
functions.http('validateTask', async (req, res) => {
  // Set CORS headers for all responses
  res.set('Access-Control-Allow-Origin', '*');
  res.set('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.set('Access-Control-Max-Age', '3600');
  
  // Handle OPTIONS requests (preflight)
  if (req.method === 'OPTIONS') {
    res.status(204).send('');
    return;
  }
  
  // Only allow POST requests
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }
  
  try {
    // Extract authentication token
    const authHeader = req.headers.authorization;
    let userId = null;
    
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.split(' ')[1];
      const decoded = verifyToken(token);
      
      if (decoded) {
        userId = decoded.id;
      }
    }
    
    const taskData = req.body;
    
    // Basic validation
    if (!taskData.title || taskData.title.trim() === '') {
      return res.status(400).json({ error: 'Task title is required' });
    }
    
    // Format and validate the task
    const validatedTask = {
      title: formatTitle(taskData.title),
      description: taskData.description ? taskData.description.trim() : '',
      completed: taskData.completed || false,
      createdAt: new Date(),
      dueDate: taskData.dueDate ? new Date(taskData.dueDate) : null,
      userId: userId // Associate task with user if authenticated
    };
    
    // Check if due date is valid
    if (taskData.dueDate) {
      const dueDate = new Date(taskData.dueDate);
      if (isNaN(dueDate.getTime())) {
        return res.status(400).json({ error: 'Invalid due date format' });
      }
    }
    
    // Connect to MongoDB if user is authenticated
    if (userId) {
      try {
        await connectToMongoDB();
        
        // Insert task into database
        const result = await db.collection('tasks').insertOne(validatedTask);
        
        // Return the created task with database ID
        res.status(200).json({
          ...validatedTask,
          id: result.insertedId,
          createdAt: validatedTask.createdAt.toISOString(),
          dueDate: validatedTask.dueDate ? validatedTask.dueDate.toISOString() : null
        });
        
      } catch (dbError) {
        console.error('Database error:', dbError);
        // If DB fails, fall back to returning the validated task without saving
        res.status(200).json({
          ...validatedTask,
          id: `task_${uuidv4()}`,
          createdAt: validatedTask.createdAt.toISOString(),
          dueDate: validatedTask.dueDate ? validatedTask.dueDate.toISOString() : null
        });
      }
    } else {
      // For unauthenticated users, just return the validated task with a UUID
      res.status(200).json({
        ...validatedTask,
        id: `task_${uuidv4()}`,
        createdAt: validatedTask.createdAt.toISOString(),
        dueDate: validatedTask.dueDate ? validatedTask.dueDate.toISOString() : null,
        userId: null
      });
    }
    
  } catch (error) {
    console.error('Error validating task:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * Function to get tasks for a specific user
 */
functions.http('getUserTasks', async (req, res) => {
  // Set CORS headers
  res.set('Access-Control-Allow-Origin', '*');
  res.set('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.set('Access-Control-Max-Age', '3600');
  
  // Handle OPTIONS requests
  if (req.method === 'OPTIONS') {
    res.status(204).send('');
    return;
  }
  
  // Only allow GET requests
  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }
  
  try {
    // Extract token from Authorization header
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'No token provided' });
    }
    
    const token = authHeader.split(' ')[1];
    const decoded = verifyToken(token);
    
    if (!decoded) {
      return res.status(401).json({ error: 'Invalid token' });
    }
    
    // Connect to MongoDB
    await connectToMongoDB();
    
    // Get tasks for this user
    const tasks = await db.collection('tasks')
      .find({ userId: decoded.id })
      .sort({ createdAt: -1 })
      .toArray();
    
    // Format dates for JSON response
    const formattedTasks = tasks.map(task => ({
      ...task,
      id: task._id,
      _id: undefined,
      createdAt: task.createdAt.toISOString(),
      dueDate: task.dueDate ? task.dueDate.toISOString() : null
    }));
    
    res.status(200).json(formattedTasks);
    
  } catch (error) {
    console.error('Error fetching tasks:', error);
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