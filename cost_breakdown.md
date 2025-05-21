# To-Do Cloud Application Cost Breakdown

This document provides a detailed cost analysis for the To-Do Cloud Application running on Google Cloud Platform, covering both testing and one month of deployment.

## GCP Pricing Reference

### Compute Engine Pricing (us-central1)
- e2-medium VM: $0.033174/hour
- e2-standard-2 VM: $0.067/hour
- Sustained use discount: Up to 30% for full month usage

### Google Kubernetes Engine Pricing
- GKE Standard cluster management fee: $0.10/hour per cluster
- Node compute resources: Same as Compute Engine VMs
- Autopilot mode: $0.0350/hour per vCPU, $0.0038/hour per GB

### Cloud Functions Pricing
- Invocations: First 2 million/month free, then $0.40/million
- Compute time: $0.000000648/GB-second
- Outbound data: First 5GB free, then $0.12/GB

### Cloud Storage Pricing
- Standard Storage: $0.020/GB/month for first 50TB
- Data retrieval: $0.01/10,000 Class A operations

### Network Pricing
- Outbound data transfer: First 1GB free, then $0.10/GB for 1-10TB/month
- Inbound data transfer: Free

## Detailed Monthly Deployment Cost Breakdown

| Component | Configuration | Calculation | Monthly Cost (USD) |
|-----------|---------------|-------------|-------------------|
| GKE Standard Cluster Management Fee | 1 cluster | $0.10/hour × 730 hours | $73.00 |
| GKE Nodes | 2 × e2-standard-2 (2 vCPU, 8GB) | 2 × $0.067/hour × 730 hours | $97.82 |
| Kubernetes Pods | 3 pods with resource requests | Included in node costs | $0.00 |
| Cloud Functions | Basic tier, 50,000 invocations | First 2M free | $0.00 |
| Cloud Functions Compute | 1GB instance, 128MB memory, avg. 200ms runtime | 50,000 × 0.2s × $0.000000648/GB-s × 0.125GB | $0.08 |
| MongoDB VM | e2-medium (2 vCPU, 4GB RAM) | $0.033174/hour × 730 hours | $24.22 |
| Persistent Disk | 10GB SSD for MongoDB | $0.17/GB/month × 10GB | $1.70 |
| Cloud Storage | 5GB standard storage | $0.020/GB/month × 5GB | $0.10 |
| Data Transfer | 50GB outbound | $0.10/GB × 49GB (first 1GB free) | $4.90 |
| **Total Monthly Deployment Cost** | | | **$201.82** |

## Detailed Testing Cost Breakdown

| Experiment | Duration | Resources Used | Calculation | Cost (USD) |
|------------|----------|----------------|-------------|------------|
| Basic Load Testing | 30 minutes | 2 GKE nodes, 3 pods, minimal function calls | (2 × $0.067/hour × 0.5 hour) + ($0.10/hour × 0.5 hour) + (50 × $0.000000648/GB-s × 0.2s × 0.125GB) | $0.12 |
| Extended Load Testing | 2 hours | 2 GKE nodes, 3 pods, moderate function calls | (2 × $0.067/hour × 2 hours) + ($0.10/hour × 2 hours) + (5,000 × $0.000000648/GB-s × 0.2s × 0.125GB) | $0.47 |
| Stress Testing | 1 hour | 2 GKE nodes scaling to 3, intense function calls | (2.5 × $0.067/hour × 1 hour) + ($0.10/hour × 1 hour) + (20,000 × $0.000000648/GB-s × 0.2s × 0.125GB) | $0.32 |
| VM Experimentation | 2 hours | MongoDB e2-medium VM | $0.033174/hour × 2 hours | $0.07 |
| Data Transfer | Various | ~10GB total test data | $0.10/GB × 9GB (first 1GB free) | $0.90 |
| **Total Testing Cost** | ~5 hours | | | **$1.88** |

## Combined Cost Summary

| Cost Category | Amount (USD) |
|---------------|--------------|
| One-month deployment | $201.82 |
| Testing expenses | $1.88 |
| **Total Project Cost (Test + One Month)** | **$203.70** |

## Cost Optimization Recommendations

1. **Right-size the MongoDB VM**: Consider e2-small ($0.0167/hour) during development for savings of ~$12/month

2. **Implement GKE Node Autoscaling**: Scale down during off-peak hours, potentially reducing node costs by 40% (~$39/month)

3. **Use GKE Autopilot**: Consider switching to GKE Autopilot which only charges for resources used by pods, not entire nodes

4. **Cloud Function Optimization**: Batch operations to reduce invocation count and execution time

5. **Reserved Instances**: For long-term deployments, committed use discounts offer 20-57% savings on VM and GKE instances

6. **Cost-per-request analysis**: At $201.82/month with ~1.5M monthly requests, each request costs approximately $0.00013

This cost analysis demonstrates that cloud-native architectures offer precise, pay-as-you-go pricing. While the monthly operational cost is $201.82, the testing phase required only $1.88, showing how cloud resources can be provisioned on-demand and terminated when not needed, resulting in significant development-phase cost efficiency.

*Note: All prices are based on Google Cloud Platform's us-central1 region pricing as of May 2025 and are subject to change. Actual costs may vary based on usage patterns, discounts, and GCP pricing updates.* 