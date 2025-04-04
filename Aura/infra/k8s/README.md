# Kubernetes Deployment Guide for Aura

This directory contains Kubernetes manifest files for deploying Aura to a Kubernetes cluster.

## Important Security Note

**NEVER** store API keys or other sensitive information directly in Kubernetes manifest files. Always use Kubernetes Secrets to manage sensitive information.

## Managing API Keys and Secrets

Aura services require various API keys (Alpaca, News API, etc.) to function properly. Here's how to securely manage these keys in Kubernetes:

1. Create a Secret YAML file (do not commit this to the repository):

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: aura-api-keys
  namespace: aura
type: Opaque
data:
  ALPACA_API_KEY: <base64-encoded-key>
  ALPACA_API_SECRET: <base64-encoded-secret>
  NEWS_API_KEY: <base64-encoded-key>
  # Add other API keys as needed
```

2. Apply the Secret to your cluster:

```bash
kubectl apply -f aura-secrets.yaml
```

3. Reference the Secret in your Deployment files:

```yaml
env:
  - name: ALPACA_API_KEY
    valueFrom:
      secretKeyRef:
        name: aura-api-keys
        key: ALPACA_API_KEY
  - name: ALPACA_API_SECRET
    valueFrom:
      secretKeyRef:
        name: aura-api-keys
        key: ALPACA_API_SECRET
  # Add other environment variables as needed
```

## Deployment Steps

1. Set up a Kubernetes cluster (e.g., using GKE, EKS, AKS, or Minikube)
2. Create namespace:
   ```
   kubectl create namespace aura
   ```
3. Apply Secrets (as described above)
4. Apply ConfigMaps
5. Deploy infrastructure components (PostgreSQL, Kafka, InfluxDB)
6. Deploy Aura services

## Infrastructure Components

For a production deployment, you should use managed services for:

- PostgreSQL (e.g., Amazon RDS, GCP Cloud SQL)
- Kafka (e.g., Confluent Cloud, Amazon MSK)
- InfluxDB (e.g., InfluxDB Cloud)

For development/testing, you can use the provided manifests for local deployments.

## Scaling Considerations

The Aura microservices are designed to be independently scalable. Consider:

- Setting up Horizontal Pod Autoscalers for services with variable load
- Using PodDisruptionBudgets for critical services
- Implementing proper liveness and readiness probes for all services 