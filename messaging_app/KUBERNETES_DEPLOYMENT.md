# Kubernetes Deployment Guide

This guide explains how to deploy the Django messaging app to Kubernetes.

## Prerequisites

- Docker installed and running
- kubectl installed
- Kubernetes cluster running (minikube, kind, or cloud cluster)
- Docker image built for the Django app

## Quick Deployment

### Option 1: Using the deployment script (Linux/Mac/Git Bash)

```bash
./deploy.sh
```

### Option 2: Manual deployment

#### Step 1: Build the Docker image

If using minikube locally:
```bash
# Set Docker environment for minikube
eval $(minikube docker-env)

# Build the image
docker build -t django-messaging-app:latest .
```

For other Kubernetes clusters, you may need to push to a container registry:
```bash
docker build -t django-messaging-app:latest .
docker tag django-messaging-app:latest <registry>/django-messaging-app:latest
docker push <registry>/django-messaging-app:latest
```

Then update the `image` field in `deployment.yaml` to use your registry image.

#### Step 2: Apply the deployment

```bash
kubectl apply -f deployment.yaml
```

#### Step 3: Verify the deployment

Check pods:
```bash
kubectl get pods
```

Check service:
```bash
kubectl get service django-messaging-app-service
```

Check deployment:
```bash
kubectl get deployment django-messaging-app
```

#### Step 4: View logs

View logs for all pods:
```bash
kubectl logs -l app=django-messaging-app
```

View logs for a specific pod:
```bash
# First get the pod name
kubectl get pods

# Then view logs
kubectl logs <pod-name>
```

## Configuration

The deployment includes:
- **Deployment**: Runs 1 replica of the Django app
- **Service**: ClusterIP service exposing the app on port 8000 internally
- **Environment Variables**: MySQL database configuration

### Environment Variables

The deployment uses the following environment variables (can be modified in `deployment.yaml`):
- `MYSQL_DB`: Database name (default: messaging_db)
- `MYSQL_USER`: Database user (default: messaging_user)
- `MYSQL_PASSWORD`: Database password (default: messaging_password)
- `MYSQL_HOST`: Database host (default: db)
- `MYSQL_PORT`: Database port (default: 3306)

**Note**: For production, consider using Kubernetes Secrets for sensitive data like passwords.

## Troubleshooting

### Pod not starting

Check pod status:
```bash
kubectl describe pod <pod-name>
```

### View pod events

```bash
kubectl get events --sort-by=.metadata.creationTimestamp
```

### Access pod shell

```bash
kubectl exec -it <pod-name> -- /bin/bash
```

### Delete and redeploy

```bash
kubectl delete -f deployment.yaml
kubectl apply -f deployment.yaml
```

## Database Considerations

**Important**: This deployment assumes you have a MySQL database available. You may need to:
1. Deploy a MySQL database separately in Kubernetes
2. Use an external database service
3. Update the `MYSQL_HOST` environment variable to point to your database service

## Scaling

To scale the deployment:
```bash
kubectl scale deployment django-messaging-app --replicas=3
```

## Cleanup

To remove the deployment:
```bash
kubectl delete -f deployment.yaml
```
