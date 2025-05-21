import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  CssBaseline, 
  AppBar, 
  Toolbar, 
  Button,
  CircularProgress
} from '@mui/material';
import AddTask from './components/AddTask';
import TaskList from './components/TaskList';
import Auth from './components/Auth';
import { Task } from './types/Task';
import { validateTask, fetchUserTasks } from './services/taskService';

// Define UserData interface
interface UserData {
  id: string;
  name: string;
  email: string;
}

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [userData, setUserData] = useState<UserData | null>(null);
  const [authChecking, setAuthChecking] = useState(true);

  // Check if user is already authenticated
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      verifyToken(token);
    } else {
      setAuthChecking(false);
    }
  }, []);

  // Verify token validity
  const verifyToken = async (token: string) => {
    try {
      const response = await fetch(
        'https://us-central1-todo-cloud-app-20250521.cloudfunctions.net/verifyToken',
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        handleLoginSuccess(token, data.user);
      } else {
        // Token is invalid, clear it
        localStorage.removeItem('authToken');
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Token verification failed:', error);
    } finally {
      setAuthChecking(false);
    }
  };

  // Load tasks after authentication
  useEffect(() => {
    if (isAuthenticated && authToken) {
      loadUserTasks();
    }
  }, [isAuthenticated, authToken]);

  // Function to load user tasks from the database
  const loadUserTasks = async () => {
    if (!authToken) return;

    try {
      setLoading(true);
      const userTasks = await fetchUserTasks(authToken);
      setTasks(userTasks);
    } catch (error) {
      console.error('Error loading tasks:', error);
      // If API fails, try to load from localStorage
      const savedTasks = localStorage.getItem('tasks');
      if (savedTasks) {
        setTasks(JSON.parse(savedTasks));
      }
    } finally {
      setLoading(false);
    }
  };

  // Save tasks to localStorage as backup
  useEffect(() => {
    if (tasks.length > 0) {
      localStorage.setItem('tasks', JSON.stringify(tasks));
    }
  }, [tasks]);

  const handleLoginSuccess = (token: string, user: UserData) => {
    setAuthToken(token);
    setUserData(user);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setAuthToken(null);
    setUserData(null);
    setIsAuthenticated(false);
    setTasks([]);
  };

  const handleAddTask = async (taskData: Omit<Task, 'id' | 'createdAt'>) => {
    try {
      setLoading(true);
      // Use our task validation service which will call the serverless function
      const validatedTask = await validateTask(taskData, authToken);
      setTasks(prev => [...prev, validatedTask]);
    } catch (error) {
      console.error('Error adding task:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleComplete = (id: string) => {
    setTasks(prev =>
      prev.map(task =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };

  const handleDeleteTask = (id: string) => {
    setTasks(prev => prev.filter(task => task.id !== id));
  };

  // Show loading indicator while checking authentication
  if (authChecking) {
    return (
      <Box 
        sx={{ 
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh'
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // Show authentication screen if not authenticated
  if (!isAuthenticated) {
    return <Auth onLogin={handleLoginSuccess} />;
  }

  return (
    <>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Typography variant="h6">
            Task Manager
          </Typography>
          <Box>
            {userData && (
              <Typography variant="body2" component="span" sx={{ mr: 2 }}>
                Hello, {userData.name}
              </Typography>
            )}
            <Button color="inherit" onClick={handleLogout}>
              Logout
            </Button>
          </Box>
        </Toolbar>
      </AppBar>
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Box sx={{ my: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            My To-Do List
          </Typography>
          <AddTask onAddTask={handleAddTask} />
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TaskList
              tasks={tasks}
              onToggleComplete={handleToggleComplete}
              onDeleteTask={handleDeleteTask}
            />
          )}
        </Box>
      </Container>
    </>
  );
}

export default App;
