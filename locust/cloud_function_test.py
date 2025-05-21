import random
import time
import uuid
from locust import HttpUser, task, between, events

# Constants
CLOUD_FUNCTION_URL = "https://us-central1-todo-cloud-app-20250521.cloudfunctions.net"

# Global stats
class CustomStats:
    def __init__(self):
        self.validation_times = []
        
    def clear(self):
        self.validation_times = []
        
    def get_avg_validation_time(self):
        return sum(self.validation_times) / len(self.validation_times) if self.validation_times else 0

stats = CustomStats()

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print(f"Starting Cloud Function load test with {environment.runner.user_count} users")
    stats.clear()

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n=== Cloud Function Test Results ===")
    print(f"Average validation time: {stats.get_avg_validation_time():.4f} seconds")
    print("==================================\n")

class CloudFunctionUser(HttpUser):
    """This user class tests the Cloud Function directly with high load"""
    wait_time = between(0.1, 1)  # More aggressive timing to stress test
    host = CLOUD_FUNCTION_URL
    
    @task
    def validate_task(self):
        """Directly test the serverless function under load"""
        # Generate random task data with a mix of capitalization
        title_options = [
            f"task {random.randint(1, 1000)}",  # lowercase
            f"Task {random.randint(1, 1000)}",  # Title case
            f"TASK {random.randint(1, 1000)}",  # ALL CAPS
        ]
        
        task_data = {
            "title": random.choice(title_options),
            "description": f"Auto-generated task from load test at {time.time()}",
            "completed": random.choice([True, False]),
            "dueDate": None
        }
        
        # Directly call the Cloud Function
        start_time = time.time()
        with self.client.post(
            "/validateTask",
            json=task_data,
            catch_response=True
        ) as response:
            validation_time = time.time() - start_time
            stats.validation_times.append(validation_time)
            
            if response.status_code == 200:
                validated_task = response.json()
                # Verify the task title has been capitalized correctly
                if validated_task['title'][0].isupper():
                    response.success()
                    print(f"Task validated: {validated_task['title']} (in {validation_time:.3f}s)")
                else:
                    response.failure(f"Task title not properly capitalized: {validated_task['title']}")
            else:
                response.failure(f"Cloud Function failed: {response.text}") 