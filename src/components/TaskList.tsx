import React from 'react';
import { 
  List, 
  ListItem, 
  ListItemText, 
  Checkbox, 
  IconButton, 
  Paper,
  Typography,
  Divider,
  ListItemSecondaryAction,
  Chip
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { Task } from '../types/Task';

interface TaskListProps {
  tasks: Task[];
  onToggleComplete: (id: string) => void;
  onDeleteTask: (id: string) => void;
}

const TaskList: React.FC<TaskListProps> = ({ 
  tasks, 
  onToggleComplete, 
  onDeleteTask 
}) => {
  // Format date to be more readable
  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  return (
    <Paper>
      <Typography variant="h6" sx={{ p: 2 }}>
        My Tasks ({tasks.length})
      </Typography>
      <Divider />
      {tasks.length === 0 ? (
        <Typography variant="body1" sx={{ p: 2, textAlign: 'center' }}>
          No tasks yet. Add one above!
        </Typography>
      ) : (
        <List>
          {tasks.map((task) => (
            <ListItem key={task.id} divider>
              <Checkbox
                edge="start"
                checked={task.completed}
                onChange={() => onToggleComplete(task.id)}
                color="primary"
              />
              <ListItemText
                primary={task.title}
                secondary={
                  <>
                    {task.description && (
                      <Typography
                        component="span"
                        variant="body2"
                        color="textPrimary"
                        display="block"
                      >
                        {task.description}
                      </Typography>
                    )}
                    <Typography
                      component="span"
                      variant="body2"
                      color="textSecondary"
                    >
                      Created: {formatDate(task.createdAt)}
                    </Typography>
                    {task.dueDate && (
                      <Chip 
                        size="small" 
                        label={`Due: ${formatDate(task.dueDate)}`} 
                        color="primary" 
                        variant="outlined"
                        sx={{ ml: 1 }}
                      />
                    )}
                  </>
                }
                sx={{
                  textDecoration: task.completed ? 'line-through' : 'none',
                }}
              />
              <ListItemSecondaryAction>
                <IconButton 
                  edge="end" 
                  aria-label="delete" 
                  onClick={() => onDeleteTask(task.id)}
                >
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      )}
    </Paper>
  );
};

export default TaskList; 