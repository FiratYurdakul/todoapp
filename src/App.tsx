import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, CssBaseline, AppBar, Toolbar } from '@mui/material';
import AddTask from './components/AddTask';
import TaskList from './components/TaskList';
import { Task } from './types/Task';
import { validateTask } from './services/taskService';

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);

  // Simulate fetching tasks from API
  useEffect(() => {
    // For now we'll use localStorage, later we'll connect to serverless functions
    const savedTasks = localStorage.getItem('tasks');
    if (savedTasks) {
      setTasks(JSON.parse(savedTasks));
    }
  }, []);

  // Save tasks to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('tasks', JSON.stringify(tasks));
  }, [tasks]);

  const handleAddTask = async (taskData: Omit<Task, 'id' | 'createdAt'>) => {
    try {
      setLoading(true);
      // Use our task validation service which will call the serverless function
      const validatedTask = await validateTask(taskData);
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

  return (
    <>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6">
            Task Manager
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Box sx={{ my: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            My To-Do List
          </Typography>
          <AddTask onAddTask={handleAddTask} />
          <TaskList
            tasks={tasks}
            onToggleComplete={handleToggleComplete}
            onDeleteTask={handleDeleteTask}
          />
        </Box>
      </Container>
    </>
  );
}

export default App;
