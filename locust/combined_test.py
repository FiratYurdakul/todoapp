import random
import time
import uuid
from locust import HttpUser, task, between, events

# Constants
FRONTEND_URL = "http://35.239.33.10"  # GKE Frontend URL
CLOUD_FUNCTION_URL = "https://us-central1-todo-cloud-app-20250521.cloudfunctions.net"  # Cloud Function

# Global stats
class CombinedStats:
    def __init__(self):
        self.frontend_times = []
        self.cloud_function_times = []
        
    def clear(self):
        self.frontend_times = []
        self.cloud_function_times = []
        
    def get_avg_frontend_time(self):
        return sum(self.frontend_times) / len(self.frontend_times) if self.frontend_times else 0
        
    def get_avg_cloud_function_time(self):
        return sum(self.cloud_function_times) / len(self.cloud_function_times) if self.cloud_function_times else 0
        
    def get_total_requests(self):
        return len(self.frontend_times) + len(self.cloud_function_times)

stats = CombinedStats()

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print(f"Starting Combined Test with {environment.runner.user_count} users")
    stats.clear()

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n=== Combined Test Results ===")
    print(f"Total Requests: {stats.get_total_requests()}")
    print(f"Average Frontend Response Time: {stats.get_avg_frontend_time():.4f} seconds")
    print(f"Average Cloud Function Response Time: {stats.get_avg_cloud_function_time():.4f} seconds")
    print("=============================\n")

class FrontendUser(HttpUser):
    """This user class tests the frontend running on GKE"""
    wait_time = between(1, 3)  # More realistic user behavior
    host = FRONTEND_URL
    
    @task(4)
    def view_homepage(self):
        """Test loading the homepage - most common operation"""
        start_time = time.time()
        with self.client.get("/", catch_response=True) as response:
            load_time = time.time() - start_time
            stats.frontend_times.append(load_time)
            
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to load homepage: {response.status_code}")
    
    @task(1)
    def simulate_task_actions(self):
        """Simulate various task actions"""
        start_time = time.time()
        with self.client.get("/", catch_response=True) as response:
            action_time = time.time() - start_time
            stats.frontend_times.append(action_time)
            
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to simulate task action: {response.status_code}")

class CloudFunctionUser(HttpUser):
    """This user class tests the Cloud Function directly"""
    wait_time = between(0.5, 2)  # Slightly more frequent than frontend
    host = CLOUD_FUNCTION_URL
    
    @task
    def validate_task(self):
        """Test the serverless task validation function"""
        # Generate random task data
        task_data = {
            "title": f"Task {random.randint(1, 1000)}",
            "description": f"Test task created at {time.time()}",
            "completed": random.choice([True, False]),
            "dueDate": None
        }
        
        # Call the Cloud Function
        start_time = time.time()
        with self.client.post("/validateTask", json=task_data, catch_response=True) as response:
            cf_time = time.time() - start_time
            stats.cloud_function_times.append(cf_time)
            
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Cloud Function failed: {response.text}") 