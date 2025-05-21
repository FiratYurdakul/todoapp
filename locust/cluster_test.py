import random
import time
import uuid
from locust import HttpUser, task, between, events

# Constants
FRONTEND_URL = "http://35.239.33.10"  # GKE Frontend URL

# Global stats
class ClusterStats:
    def __init__(self):
        self.page_load_times = []
        self.create_task_times = []
        self.view_task_times = []
        self.delete_task_times = []
        
    def clear(self):
        self.page_load_times = []
        self.create_task_times = []
        self.view_task_times = []
        self.delete_task_times = []
        
    def get_avg_page_load_time(self):
        return sum(self.page_load_times) / len(self.page_load_times) if self.page_load_times else 0
        
    def get_avg_create_task_time(self):
        return sum(self.create_task_times) / len(self.create_task_times) if self.create_task_times else 0
        
    def get_avg_view_task_time(self):
        return sum(self.view_task_times) / len(self.view_task_times) if self.view_task_times else 0
        
    def get_avg_delete_task_time(self):
        return sum(self.delete_task_times) / len(self.delete_task_times) if self.delete_task_times else 0

stats = ClusterStats()

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print(f"Starting GKE Cluster load test with {environment.runner.user_count} users")
    stats.clear()

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n=== GKE Cluster Test Results ===")
    print(f"Average page load time: {stats.get_avg_page_load_time():.4f} seconds")
    print(f"Average task creation time: {stats.get_avg_create_task_time():.4f} seconds")
    print(f"Average task view time: {stats.get_avg_view_task_time():.4f} seconds")
    print(f"Average task deletion time: {stats.get_avg_delete_task_time():.4f} seconds")
    print("================================\n")

class FrontendUser(HttpUser):
    """This user class tests the frontend running on GKE"""
    wait_time = between(1, 3)  # More realistic user behavior
    host = FRONTEND_URL
    
    @task(3)
    def view_homepage(self):
        """Test loading the homepage - most common operation"""
        start_time = time.time()
        with self.client.get("/", catch_response=True) as response:
            load_time = time.time() - start_time
            stats.page_load_times.append(load_time)
            
            if response.status_code == 200:
                print(f"Homepage loaded in {load_time:.3f}s")
                response.success()
            else:
                response.failure(f"Failed to load homepage: {response.status_code}")
    
    @task(2)
    def simulate_task_creation(self):
        """Simulate creating a new task"""
        start_time = time.time()
        # In a real app with API endpoints, we'd POST to create a task
        # For now we're just measuring roundtrip page loads to stress test the cluster
        with self.client.get("/", catch_response=True) as response:
            create_time = time.time() - start_time
            stats.create_task_times.append(create_time)
            
            if response.status_code == 200:
                print(f"Task creation simulated in {create_time:.3f}s")
                response.success()
            else:
                response.failure(f"Failed to simulate task creation: {response.status_code}")
    
    @task(1)
    def simulate_view_task(self):
        """Simulate viewing a task's details"""
        start_time = time.time()
        with self.client.get("/", catch_response=True) as response:
            view_time = time.time() - start_time
            stats.view_task_times.append(view_time)
            
            if response.status_code == 200:
                print(f"Task view simulated in {view_time:.3f}s")
                response.success()
            else:
                response.failure(f"Failed to simulate task view: {response.status_code}")
    
    @task(1)
    def simulate_delete_task(self):
        """Simulate deleting a task"""
        start_time = time.time()
        with self.client.get("/", catch_response=True) as response:
            delete_time = time.time() - start_time
            stats.delete_task_times.append(delete_time)
            
            if response.status_code == 200:
                print(f"Task deletion simulated in {delete_time:.3f}s")
                response.success()
            else:
                response.failure(f"Failed to simulate task deletion: {response.status_code}") 