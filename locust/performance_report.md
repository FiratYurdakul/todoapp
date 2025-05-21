# Cloud-Native To-Do Application Performance Report

## Test Environment

- **Cloud Provider:** Google Cloud Platform
- **Infrastructure Components:**
  - Frontend: GKE (Google Kubernetes Engine) - 3 pods for horizontal scaling
  - Serverless Function: Google Cloud Functions (2nd Gen)
  - Database: MongoDB on Compute Engine VM (e2-medium)
- **Test Tool:** Locust
- **Test Duration:** 10 minutes
- **User Load:**
  - 100 concurrent users
  - Ramp-up rate: 10 users/second

## Test Scenarios

1. **Viewing Tasks (Frontend):**
   - Simulates users browsing their task lists
   - Most common operation (60% of traffic)

2. **Task Creation with Validation (Serverless Function):**
   - Tests the Cloud Function that validates and formats task data
   - Medium frequency operation (30% of traffic)

3. **Task Updates (Frontend + Database):**
   - Toggles task completion status
   - Low frequency operation (5% of traffic)

4. **Task Deletion (Frontend + Database):**
   - Removes a task from the list
   - Lowest frequency operation (5% of traffic)

## Performance Metrics

### Response Time

| Operation | Min (ms) | Max (ms) | Mean (ms) | Median (ms) | 95th Percentile (ms) |
|-----------|----------|----------|-----------|-------------|----------------------|
| View Tasks | TBD | TBD | TBD | TBD | TBD |
| Create Task (Cloud Function) | TBD | TBD | TBD | TBD | TBD |
| Update Task | TBD | TBD | TBD | TBD | TBD |
| Delete Task | TBD | TBD | TBD | TBD | TBD |

### Throughput

| Component | Requests/Second | Failed Requests (%) |
|-----------|-----------------|---------------------|
| Frontend | TBD | TBD |
| Cloud Function | TBD | TBD |
| Overall System | TBD | TBD |

### Resource Utilization

| Component | CPU (Avg %) | Memory (Avg %) | Network I/O (MB/s) |
|-----------|-------------|----------------|-------------------|
| GKE Pods | TBD | TBD | TBD |
| Cloud Function | TBD | TBD | TBD |
| MongoDB VM | TBD | TBD | TBD |

### Error Rates

| Component | Error Count | Error Rate (%) | Most Common Error |
|-----------|-------------|----------------|-------------------|
| Frontend | TBD | TBD | TBD |
| Cloud Function | TBD | TBD | TBD |
| MongoDB | TBD | TBD | TBD |

## Bottlenecks Identified

1. TBD
2. TBD
3. TBD

## Scaling Behavior

- **Frontend (GKE):** TBD
- **Cloud Function:** TBD
- **Database (VM):** TBD

## Cost Analysis

| Component | Instance Type | Monthly Cost Estimate |
|-----------|---------------|------------------------|
| GKE Cluster | TBD | TBD |
| Cloud Function | TBD | TBD |
| MongoDB VM | e2-medium | TBD |
| Network/Other | N/A | TBD |
| **Total** | | **TBD** |

## Conclusions

TBD

## Recommendations

1. TBD
2. TBD
3. TBD 