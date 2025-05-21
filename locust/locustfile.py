import json
import random
from locust import HttpUser, task, between

class TodoUser(HttpUser):
    wait_time = between(1, 5)  # Wait between 1 and 5 seconds between tasks
    
    def on_start(self):
        # Initialize user-specific data
        self.task_titles = [
            "Buy groceries",
            "Finish project report",
            "Call dentist",
            "Schedule team meeting",
            "Pay bills",
            "Clean the garage",
            "Go for a run",
            "Read book chapter",
            "Water plants",
            "Review code PR"
        ]
        self.descriptions = [
            "Need to get milk, eggs, and bread",
            "The quarterly report is due next week",
            "Schedule regular checkup",
            "Discuss project timeline with team",
            "Electricity and internet bills",
            "It's getting messy in there",
            "Aim for 5k today",
            "Chapter 7 of 'Clean Code'",
            "Don't forget the plants on the balcony",
            "Review the bug fix PR from John"
        ]
    
    @task(10)
    def get_tasks(self):
        """Simulate a user viewing their tasks"""
        self.client.get("/api/tasks")
    
    @task(5)
    def add_task(self):
        """Simulate a user adding a new task"""
        idx = random.randint(0, len(self.task_titles) - 1)
        task_data = {
            "title": self.task_titles[idx],
            "description": self.descriptions[idx],
            "completed": False,
            "dueDate": None
        }
        
        # First call the validation function
        with self.client.post(
            "/api/validate-task",
            json=task_data,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                validated_task = response.json()
                # Then create the task with the validated data
                self.client.post("/api/tasks", json=validated_task)
            else:
                response.failure(f"Failed to validate task: {response.text}")
    
    @task(3)
    def toggle_task(self):
        """Simulate a user marking a task as complete/incomplete"""
        # First get all tasks to find one to toggle
        with self.client.get("/api/tasks", catch_response=True) as response:
            if response.status_code == 200:
                tasks = response.json()
                if tasks:
                    # Pick a random task
                    task = random.choice(tasks)
                    task_id = task["id"]
                    # Toggle the completed status
                    task["completed"] = not task["completed"]
                    # Update the task
                    self.client.put(f"/api/tasks/{task_id}", json=task)
    
    @task(1)
    def delete_task(self):
        """Simulate a user deleting a task"""
        # First get all tasks to find one to delete
        with self.client.get("/api/tasks", catch_response=True) as response:
            if response.status_code == 200:
                tasks = response.json()
                if tasks:
                    # Pick a random task
                    task = random.choice(tasks)
                    task_id = task["id"]
                    # Delete the task
                    self.client.delete(f"/api/tasks/{task_id}") 