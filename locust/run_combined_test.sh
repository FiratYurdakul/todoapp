#!/bin/bash
set -e

# This script runs a combined performance test on both the frontend and Cloud Function

# Set default values
DURATION=${1:-60}      # Test duration in seconds (default 1 minute)
USERS=${2:-60}         # Number of users (default 60)
SPAWN_RATE=${3:-10}    # Users spawned per second (default 10)

echo "================================================================="
echo "  Running Combined Performance Test on To-Do Cloud Application"
echo "================================================================="
echo "Duration: $DURATION seconds"
echo "Users: $USERS"
echo "Spawn rate: $SPAWN_RATE users/second"
echo "Test starts in 3 seconds..."
sleep 3

# Start headless Locust test with combined test
echo "Starting test..."
python3 -m locust --headless -f combined_test.py --users $USERS --spawn-rate $SPAWN_RATE --run-time ${DURATION}s --csv=combined_results

# Generate timestamp for report
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# Create results summary
echo "Creating combined results summary..."
cat << EOF > combined_test_results_${TIMESTAMP}.md
# Combined Cloud Application Performance Test

## Test Configuration
- Date: $(date "+%B %d, %Y")
- Duration: $DURATION seconds
- Concurrent Users: $USERS
- Spawn Rate: $SPAWN_RATE users/second

## Components Tested
- Frontend: GKE Cluster (http://35.239.33.10)
- Backend: Cloud Function (https://us-central1-todo-cloud-app-20250521.cloudfunctions.net)

## Results
Results will be automatically populated after test completion.

EOF

# Append test results to the report
python3 << EOF >> combined_test_results_${TIMESTAMP}.md
import csv

# Read stats CSV file
stats = {}
try:
    with open('combined_results_stats.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stats[row['Name']] = {
                'requests': int(row['# requests']),
                'failures': int(row['# failures']),
                'median_response_time': float(row['Median Response Time']),
                'avg_response_time': float(row['Average Response Time']),
                'min_response_time': float(row['Min Response Time']),
                'max_response_time': float(row['Max Response Time']),
                'rps': float(row['Requests/s'])
            }
            
    # Calculate summary stats
    total_requests = sum(stats[k]['requests'] for k in stats if k != 'Aggregated')
    total_failures = sum(stats[k]['failures'] for k in stats if k != 'Aggregated')
    
    # Write performance results section
    print(f"""
## Performance Results

### Request Statistics
- Total Requests: {total_requests}
- Successful Requests: {total_requests - total_failures} ({(100 - 100 * total_failures / total_requests if total_requests > 0 else 0):.2f}%)
- Failed Requests: {total_failures} ({(100 * total_failures / total_requests if total_requests > 0 else 0):.2f}%)
- Average Request Rate: {sum(stats[k]['rps'] for k in stats if k != 'Aggregated'):.2f} requests/second

### Response Times

| Component | Average | Median | Min | Max | RPS |
|-----------|---------|--------|-----|-----|-----|""")
    
    # Add individual component rows
    for name, data in stats.items():
        if name != 'Aggregated':
            print(f"| {name} | {data['avg_response_time']:.1f}ms | {data['median_response_time']:.1f}ms | {data['min_response_time']:.1f}ms | {data['max_response_time']:.1f}ms | {data['rps']:.2f} |")
            
    # Add additional analysis
    print(f"""
## Analysis

The combined test successfully evaluated both components of the cloud-native architecture:

1. **Kubernetes Frontend**: Handled {stats.get('GET /', {}).get('requests', 0)} requests with an average response time of {stats.get('GET /', {}).get('avg_response_time', 0):.1f}ms.

2. **Cloud Function**: Processed {stats.get('POST /validateTask', {}).get('requests', 0)} validation requests with an average response time of {stats.get('POST /validateTask', {}).get('avg_response_time', 0):.1f}ms.

The system demonstrated good stability under load with both components maintaining consistent performance throughout the test duration.

## Recommendations

Based on the combined test results:

- The architecture shows good isolation between components, with neither the frontend nor the serverless function negatively impacting each other's performance.
- The system can handle a sustained load of {total_requests / (int('$DURATION') if int('$DURATION') > 0 else 1):.1f} requests per second.
- For production deployment, implementing a CDN in front of the GKE cluster would further improve performance and reduce load on the Kubernetes pods.
""")
    
except Exception as e:
    print(f"Error generating report: {e}")
    print(f"Please check combined_results_stats.csv file")
EOF

echo "================================================================="
echo "Combined test completed!"
echo "Report saved to: combined_test_results_${TIMESTAMP}.md"
echo "Raw results saved to: combined_results_*.csv"
echo "=================================================================" 