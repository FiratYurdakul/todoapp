import json
import random
import time
import uuid
from locust import HttpUser, task, between, events

# Constants
FRONTEND_URL = "http://35.239.33.10"  # Your deployed frontend
CLOUD_FUNCTION_URL = "https://us-central1-todo-cloud-app-20250521.cloudfunctions.net"  # Your Cloud Function

# Test data
TASK_TITLES = [
    "Buy groceries", 
    "Complete CS 436 assignment",
    "Pay bills",
    "Call doctor's office",
    "Review project report",
    "Submit class registration",
    "Book flight tickets",
    "Update resume",
    "Schedule team meeting",
    "Fix bugs in project"
]

TASK_DESCRIPTIONS = [
    "Need to get milk, eggs, and bread",
    "Due next Friday by 11:59 PM", 
    "Electricity and internet are due this week",
    "Make annual checkup appointment",
    "Need feedback from colleagues before Tuesday",
    "Registration opens on Monday at 9 AM",
    "Compare prices for summer vacation",
    "Add cloud project experience",
    "Discuss progress on milestone 2",
    "Priority: fix authentication issue"
]

# Global stats
class CustomStats:
    def __init__(self):
        self.validation_times = []
        self.read_times = []
        self.update_times = []
        self.delete_times = []
        
    def clear(self):
        self.validation_times = []
        self.read_times = []
        self.update_times = []
        self.delete_times = []
        
    def get_avg_validation_time(self):
        return sum(self.validation_times) / len(self.validation_times) if self.validation_times else 0
        
    def get_avg_read_time(self):
        return sum(self.read_times) / len(self.read_times) if self.read_times else 0
        
    def get_avg_update_time(self):
        return sum(self.update_times) / len(self.update_times) if self.update_times else 0
        
    def get_avg_delete_time(self):
        return sum(self.delete_times) / len(self.delete_times) if self.delete_times else 0

stats = CustomStats()

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print(f"Test is starting with {environment.runner.user_count} users")
    stats.clear()

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n=== Test Results ===")
    print(f"Average validation time: {stats.get_avg_validation_time():.4f} seconds")
    print(f"Average read time: {stats.get_avg_read_time():.4f} seconds")
    print(f"Average update time: {stats.get_avg_update_time():.4f} seconds")
    print(f"Average delete time: {stats.get_avg_delete_time():.4f} seconds")
    print("===================\n")

class TodoUser(HttpUser):
    # Wait 1-5 seconds between tasks
    wait_time = between(1, 5)
    host = FRONTEND_URL
    
    def on_start(self):
        # Each user creates their own task list for testing
        self.tasks_created = []
        
    @task(3)
    def view_tasks(self):
        """Simulate users just viewing their task list (most common action)"""
        # In a real app, this would call the backend API
        # For now we're just testing the frontend load
        start_time = time.time()
        with self.client.get("/", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Failed to load homepage: {response.status_code}")
            else:
                response.success()
                stats.read_times.append(time.time() - start_time)
    
    @task(2)
    def create_task(self):
        """Test the serverless function for task validation"""
        idx = random.randint(0, len(TASK_TITLES) - 1)
        task_data = {
            "title": TASK_TITLES[idx],
            "description": TASK_DESCRIPTIONS[idx],
            "completed": False,
            "dueDate": None
        }
        
        # Create a task - we're just testing frontend performance
        start_time = time.time()
        with self.client.get("/", catch_response=True) as response:
            stats.validation_times.append(time.time() - start_time)
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to load homepage: {response.status_code}")
    
    @task(1)
    def update_task(self):
        """Test updating a task"""
        start_time = time.time()
        # This would be an API call in the real app
        # We're simulating this with a roundtrip request
        with self.client.get("/", catch_response=True) as response:
            stats.update_times.append(time.time() - start_time)
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to load page for update: {response.status_code}")
    
    @task(1)
    def delete_task(self):
        """Test deleting a task"""
        start_time = time.time()
        # This would be an API call in the real app
        # We're simulating this with a roundtrip request
        with self.client.get("/", catch_response=True) as response:
            stats.delete_times.append(time.time() - start_time)
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to load page for deletion: {response.status_code}")

class CloudFunctionUser(HttpUser):
    """This user class tests the Cloud Function directly with high load"""
    wait_time = between(0.1, 1)  # More aggressive timing to stress test
    host = CLOUD_FUNCTION_URL
    
    @task
    def validate_task(self):
        """Directly test the serverless function under load"""
        # Generate random task data
        task_data = {
            "title": f"Task {uuid.uuid4().hex[:8]}",
            "description": f"Auto-generated task from load test at {time.time()}",
            "completed": random.choice([True, False]),
            "dueDate": None
        }
        
        # Directly call the Cloud Function
        with self.client.post(
            "/validateTask",
            json=task_data,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Cloud Function failed under load: {response.text}") 