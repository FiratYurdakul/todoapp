import json
import random
import time
import uuid
from locust import HttpUser, task, between, events

# Constants
FRONTEND_URL = "http://35.239.33.10"  # Your GKE deployed frontend URL
AUTH_FUNCTION_URL = "https://us-central1-todo-cloud-app-20250521.cloudfunctions.net"  # Base URL for auth functions
TASK_FUNCTION_URL = "https://us-central1-todo-cloud-app-20250521.cloudfunctions.net"  # Base URL for task functions

# Names for signup
FIRST_NAMES = ["Alex", "Jamie", "Taylor", "Jordan", "Casey", "Riley", "Morgan", "Avery", "Peyton", "Quinn", "Blake", "Dakota"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson", "Anderson", "Taylor", "Thomas", "Garcia"]

# Global stats for measuring performance
class AuthStats:
    def __init__(self):
        self.signup_times = []
        self.login_times = []
        self.token_verify_times = []
        self.create_task_times = []
        self.get_tasks_times = []
        
    def clear(self):
        self.signup_times = []
        self.login_times = []
        self.token_verify_times = []
        self.create_task_times = []
        self.get_tasks_times = []
        
    def get_avg(self, times_list):
        return sum(times_list) / len(times_list) if times_list else 0

stats = AuthStats()

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print(f"Starting Authentication Load Test with {environment.runner.user_count} users")
    stats.clear()

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n=== Authentication Load Test Results ===")
    print(f"Average Signup Time: {stats.get_avg(stats.signup_times):.4f} seconds")
    print(f"Average Login Time: {stats.get_avg(stats.login_times):.4f} seconds")
    print(f"Average Token Verification Time: {stats.get_avg(stats.token_verify_times):.4f} seconds")
    print(f"Average Create Task Time: {stats.get_avg(stats.create_task_times):.4f} seconds")
    print(f"Average Get Tasks Time: {stats.get_avg(stats.get_tasks_times):.4f} seconds")
    print("====================================\n")

class AuthenticatedUser(HttpUser):
    """This user class tests the full authentication and task flow"""
    wait_time = between(1, 3)  # Realistic wait between actions
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_token = None
        self.user_id = None
        self.email = None
        self.password = "TestPassword123!"
    
    def on_start(self):
        """Each user either signs up or logs in at the start"""
        # Generate a random user for this session
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        rand_id = str(uuid.uuid4())[:8]
        self.email = f"{first_name.lower()}.{last_name.lower()}.{rand_id}@example.com"
        
        # Randomly decide whether to sign up or log in
        # 20% of users will sign up, 80% will try to log in
        if random.random() < 0.2:
            self.signup()
        else:
            self.login()
    
    def signup(self):
        """Test the signup endpoint"""
        # Create a new user
        user_data = {
            "name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            "email": self.email,
            "password": self.password
        }
        
        start_time = time.time()
        with self.client.post(
            f"{AUTH_FUNCTION_URL}/signup",
            json=user_data,
            catch_response=True
        ) as response:
            signup_time = time.time() - start_time
            stats.signup_times.append(signup_time)
            
            if response.status_code == 201:
                # Successfully signed up
                try:
                    data = response.json()
                    self.auth_token = data.get("token")
                    self.user_id = data.get("user", {}).get("id")
                    response.success()
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response from signup")
            elif response.status_code == 409:
                # User already exists, try to log in instead
                response.success()
                self.login()
            else:
                response.failure(f"Signup failed: {response.status_code} - {response.text}")
    
    def login(self):
        """Test the login endpoint"""
        # Log in with existing credentials
        login_data = {
            "email": self.email,
            "password": self.password
        }
        
        start_time = time.time()
        with self.client.post(
            f"{AUTH_FUNCTION_URL}/login",
            json=login_data,
            catch_response=True
        ) as response:
            login_time = time.time() - start_time
            stats.login_times.append(login_time)
            
            if response.status_code == 200:
                # Successfully logged in
                try:
                    data = response.json()
                    self.auth_token = data.get("token")
                    self.user_id = data.get("user", {}).get("id")
                    response.success()
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response from login")
            elif response.status_code == 401:
                # Invalid credentials, try signing up
                response.success()
                self.signup()
            else:
                response.failure(f"Login failed: {response.status_code} - {response.text}")
    
    def verify_token(self):
        """Test the token verification endpoint"""
        if not self.auth_token:
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        start_time = time.time()
        with self.client.get(
            f"{AUTH_FUNCTION_URL}/verifyToken",
            headers=headers,
            catch_response=True
        ) as response:
            verify_time = time.time() - start_time
            stats.token_verify_times.append(verify_time)
            
            if response.status_code == 200:
                # Token is valid
                response.success()
            else:
                # Token is invalid, try logging in again
                response.failure(f"Token verification failed: {response.status_code}")
                self.login()
    
    @task(1)
    def test_token_verification(self):
        """Simply test the token verification endpoint"""
        self.verify_token()
    
    @task(3)
    def get_user_tasks(self):
        """Test getting the user's tasks"""
        if not self.auth_token:
            self.login()
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        start_time = time.time()
        with self.client.get(
            f"{TASK_FUNCTION_URL}/getUserTasks",
            headers=headers,
            catch_response=True
        ) as response:
            get_time = time.time() - start_time
            stats.get_tasks_times.append(get_time)
            
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                # Token expired or invalid
                response.success()
                self.login()
            else:
                response.failure(f"Failed to get tasks: {response.status_code} - {response.text}")
    
    @task(2)
    def create_task(self):
        """Test creating a new task"""
        if not self.auth_token:
            self.login()
            return
            
        # Generate a random task
        task_data = {
            "title": f"Task {random.randint(1, 1000)}",
            "description": f"Task created during load test at {time.time()}",
            "completed": False,
            "dueDate": None
        }
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        start_time = time.time()
        with self.client.post(
            f"{TASK_FUNCTION_URL}/validateTask",
            json=task_data,
            headers=headers,
            catch_response=True
        ) as response:
            create_time = time.time() - start_time
            stats.create_task_times.append(create_time)
            
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                # Token expired or invalid
                response.success()
                self.login()
            else:
                response.failure(f"Failed to create task: {response.status_code} - {response.text}") 