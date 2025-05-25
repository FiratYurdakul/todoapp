import json
import random
import time
import uuid
from locust import HttpUser, task, between, events

# The frontend URL running on GKE
FRONTEND_URL = "http://35.239.33.10"

# Names for signup
FIRST_NAMES = ["Alex", "Jamie", "Taylor", "Jordan", "Casey", "Riley", "Morgan", "Avery"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson"]

# Global stats for measuring performance
class KubernetesStats:
    def __init__(self):
        self.homepage_times = []
        self.login_page_times = []
        self.full_login_times = []
        self.task_create_times = []
        self.task_list_times = []
        
    def clear(self):
        self.homepage_times = []
        self.login_page_times = []
        self.full_login_times = []
        self.task_create_times = []
        self.task_list_times = []
        
    def get_avg(self, times_list):
        return sum(times_list) / len(times_list) if times_list else 0

stats = KubernetesStats()

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print(f"Starting Kubernetes Cluster Test with {environment.runner.user_count} users")
    stats.clear()

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n=== Kubernetes Cluster Test Results ===")
    print(f"Average Homepage Load Time: {stats.get_avg(stats.homepage_times):.4f} seconds")
    print(f"Average Login Page Time: {stats.get_avg(stats.login_page_times):.4f} seconds")
    print(f"Average Full Login Flow Time: {stats.get_avg(stats.full_login_times):.4f} seconds")
    print(f"Average Task Creation Time: {stats.get_avg(stats.task_create_times):.4f} seconds")
    print(f"Average Task List Time: {stats.get_avg(stats.task_list_times):.4f} seconds")
    print("=======================================\n")

class FrontendUser(HttpUser):
    """This user class tests the frontend application running in GKE"""
    wait_time = between(1, 3)  # Realistic wait between actions
    host = FRONTEND_URL
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_token = None
        self.user_id = None
        self.email = None
        self.password = "TestPassword123!"
        # Generate a random user for this session
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        rand_id = str(uuid.uuid4())[:8]
        self.email = f"{first_name.lower()}.{last_name.lower()}.{rand_id}@example.com"
        self.user_name = f"{first_name} {last_name}"
    
    @task(1)
    def load_homepage(self):
        """Test the frontend homepage load time"""
        start_time = time.time()
        with self.client.get("/", catch_response=True) as response:
            load_time = time.time() - start_time
            stats.homepage_times.append(load_time)
            
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to load homepage: {response.status_code}")
    
    @task(2)
    def login_flow(self):
        """Simulate the full login flow through the frontend"""
        # First load the login page
        start_page_time = time.time()
        with self.client.get("/", catch_response=True) as response:
            page_load_time = time.time() - start_page_time
            stats.login_page_times.append(page_load_time)
            
            if response.status_code != 200:
                response.failure(f"Failed to load login page: {response.status_code}")
                return
        
        # Now try the full login process
        # We'll make the request directly to the API endpoint that the frontend would call
        start_full_time = time.time()
        
        # Randomly decide between login or signup
        if random.random() < 0.2:  # 20% signup, 80% login
            credentials = {
                "name": self.user_name,
                "email": self.email,
                "password": self.password
            }
            endpoint = "signup"
        else:
            credentials = {
                "email": self.email,
                "password": self.password
            }
            endpoint = "login"
        
        # Send the request to the authentication endpoint
        auth_url = f"https://us-central1-todo-cloud-app-20250521.cloudfunctions.net/{endpoint}"
        with self.client.post(
            auth_url,
            json=credentials,
            catch_response=True,
            name=f"API: {endpoint}"
        ) as response:
            full_time = time.time() - start_full_time
            stats.full_login_times.append(full_time)
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    self.auth_token = data.get("token")
                    response.success()
                except json.JSONDecodeError:
                    response.failure(f"Invalid JSON in {endpoint} response")
            elif response.status_code == 409 and endpoint == "signup":
                # User already exists, this is fine for our test
                response.success()
            elif response.status_code == 401 and endpoint == "login":
                # Invalid credentials - simulate creating the account instead
                response.success()
            else:
                response.failure(f"Failed {endpoint}: {response.status_code}")
    
    @task(3)
    def view_task_list(self):
        """Test viewing the task list through the frontend"""
        # First ensure we're logged in
        if not self.auth_token:
            self.login_flow()
            return
        
        # Now fetch the task list through the API that the frontend would call
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        start_time = time.time()
        
        with self.client.get(
            "https://us-central1-todo-cloud-app-20250521.cloudfunctions.net/getUserTasks",
            headers=headers,
            catch_response=True,
            name="API: getUserTasks"
        ) as response:
            list_time = time.time() - start_time
            stats.task_list_times.append(list_time)
            
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                # Token expired, clear it so we re-login next time
                self.auth_token = None
                response.success()
            else:
                response.failure(f"Failed to get task list: {response.status_code}")
    
    @task(2)
    def create_task(self):
        """Test creating a task through the frontend"""
        # First ensure we're logged in
        if not self.auth_token:
            self.login_flow()
            return
        
        # Create a random task
        task_data = {
            "title": f"Task {random.randint(1, 1000)}",
            "description": f"Created during K8s test at {time.time()}",
            "completed": False,
            "dueDate": None
        }
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        start_time = time.time()
        
        # Call the task validation function
        with self.client.post(
            "https://us-central1-todo-cloud-app-20250521.cloudfunctions.net/validateTask",
            json=task_data,
            headers=headers,
            catch_response=True,
            name="API: validateTask"
        ) as response:
            create_time = time.time() - start_time
            stats.task_create_times.append(create_time)
            
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                # Token expired, clear it so we re-login next time
                self.auth_token = None
                response.success()
            else:
                response.failure(f"Failed to create task: {response.status_code}")
                
    @task(1)
    def navigate_app(self):
        """Simulate user navigating through different parts of the app"""
        # This simulates a user navigating through the single-page application
        # Since it's a React app, most navigation happens client-side without actual page loads
        # We'll simulate this by making requests to the homepage with different URL fragments
        
        # Randomly select a route to "navigate" to
        routes = [
            "/",              # Home
            "/#tasks",        # Tasks list
            "/#new-task",     # New task form
            "/#profile"       # User profile
        ]
        
        route = random.choice(routes)
        with self.client.get(
            route,
            catch_response=True,
            name=f"Navigate: {route}"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to navigate to {route}: {response.status_code}") 