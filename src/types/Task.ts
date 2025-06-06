export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  createdAt: string;
  dueDate?: string;
  userId?: string | null;
} 