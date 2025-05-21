#!/bin/bash
set -e

# Font formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Help function
show_help() {
  echo -e "${BOLD}To-Do Cloud Application Performance Testing Suite${NC}"
  echo
  echo "Usage: $0 [test_type] [duration] [users] [spawn_rate]"
  echo
  echo "Test Types:"
  echo "  cloud      - Test the Cloud Function component"
  echo "  cluster    - Test the GKE Cluster component"
  echo "  combined   - Test both components together"
  echo "  all        - Run all test types sequentially"
  echo
  echo "Parameters:"
  echo "  duration   - Test duration in seconds (default: 30)"
  echo "  users      - Number of concurrent users (default: 30)"
  echo "  spawn_rate - User spawn rate per second (default: 10)"
  echo
  echo "Examples:"
  echo "  $0 cloud 60 50 10     # Run Cloud Function test for 60s with 50 users"
  echo "  $0 cluster            # Run GKE test with default settings"
  echo "  $0 all 30 20 5        # Run all tests with specified parameters"
  echo
}

# Default values
TEST_TYPE=${1:-"help"}
DURATION=${2:-30}
USERS=${3:-30}
SPAWN_RATE=${4:-10}

# Validate inputs
if [[ "$TEST_TYPE" == "help" || "$TEST_TYPE" == "-h" || "$TEST_TYPE" == "--help" ]]; then
  show_help
  exit 0
fi

if ! [[ "$DURATION" =~ ^[0-9]+$ ]]; then
  echo "Error: Duration must be a number"
  exit 1
fi

if ! [[ "$USERS" =~ ^[0-9]+$ ]]; then
  echo "Error: Users must be a number"
  exit 1
fi

if ! [[ "$SPAWN_RATE" =~ ^[0-9]+$ ]]; then
  echo "Error: Spawn rate must be a number"
  exit 1
fi

# Run cloud function test
run_cloud_test() {
  echo -e "\n${GREEN}======= Running Cloud Function Test =======${NC}"
  echo "Duration: $DURATION seconds, Users: $USERS, Spawn Rate: $SPAWN_RATE users/second"
  python3 -m locust -f cloud_function_test.py --host=https://us-central1-todo-cloud-app-20250521.cloudfunctions.net --headless --users $USERS --spawn-rate $SPAWN_RATE --run-time ${DURATION}s
}

# Run cluster test
run_cluster_test() {
  echo -e "\n${GREEN}======= Running GKE Cluster Test =======${NC}"
  echo "Duration: $DURATION seconds, Users: $USERS, Spawn Rate: $SPAWN_RATE users/second"
  python3 -m locust -f cluster_test.py --host=http://35.239.33.10 --headless --users $USERS --spawn-rate $SPAWN_RATE --run-time ${DURATION}s
}

# Run combined test
run_combined_test() {
  echo -e "\n${GREEN}======= Running Combined Test =======${NC}"
  echo "Duration: $DURATION seconds, Users: $USERS, Spawn Rate: $SPAWN_RATE users/second"
  python3 -m locust -f combined_test.py --headless --users $USERS --spawn-rate $SPAWN_RATE --run-time ${DURATION}s
}

# Run the selected test
case "$TEST_TYPE" in
  "cloud")
    run_cloud_test
    ;;
  "cluster")
    run_cluster_test
    ;;
  "combined")
    run_combined_test
    ;;
  "all")
    run_cloud_test
    sleep 2
    run_cluster_test
    sleep 2
    run_combined_test
    ;;
  *)
    echo -e "${BOLD}Error:${NC} Unknown test type '$TEST_TYPE'"
    show_help
    exit 1
    ;;
esac

echo -e "\n${BLUE}Test(s) completed successfully!${NC}"
echo "Check the final_performance_report.md for a comprehensive analysis" 