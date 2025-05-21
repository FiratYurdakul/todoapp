#!/bin/bash
set -e

# This script runs Locust performance tests on the To-Do app

# Set default values
DURATION=${1:-300}  # Test duration in seconds (default 5 minutes)
USERS=${2:-50}      # Number of users (default 50)
SPAWN_RATE=${3:-10} # Users spawned per second (default 10)

echo "================================================================="
echo "  Running Locust Performance Tests on To-Do Cloud Application"
echo "================================================================="
echo "Duration: $DURATION seconds"
echo "Users: $USERS"
echo "Spawn rate: $SPAWN_RATE users/second"
echo "Test starts in 3 seconds..."
sleep 3

# Start headless Locust test
echo "Starting test..."
locust --headless -f load_test.py --users $USERS --spawn-rate $SPAWN_RATE --run-time ${DURATION}s --csv=results

# Generate report
echo "Test complete. Generating report..."
echo "Raw results saved to results_*.csv files"

# Convert dates in the report
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
cp performance_report.md "performance_report_$TIMESTAMP.md"

echo "Performance test completed!"
echo "Report template saved to: performance_report_$TIMESTAMP.md"
echo "================================================================="
echo "To fill out the report with actual values, use the data from:"
echo "- results_stats.csv (response times and request counts)"
echo "- results_exceptions.csv (errors)"
echo "- GCP Monitoring dashboard for resource utilization data"
echo "=================================================================" 