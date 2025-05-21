import random
import time
import uuid
from locust import HttpUser, task, between

class CloudFunctionUser(HttpUser):
    """This user tests the Cloud Function directly"""
    wait_time = between(1, 3)
    # This will be set by --host parameter
    
    @task
    def validate_task(self):
        """Test our serverless validation function"""
        # Generate random task data
        task_data = {
            "title": f"task {random.randint(1, 1000)}",
            "description": f"Test task created at {time.time()}",
            "completed": False,
            "dueDate": None
        }
        
        # Call the Cloud Function
        response = self.client.post("/validateTask", json=task_data)
        
        # Log the result
        if response.status_code == 200:
            validated_task = response.json()
            print(f"Task validated: {validated_task['title']}")
        else:
            print(f"Error: {response.status_code} - {response.text}") 