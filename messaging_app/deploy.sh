#!/bin/bash

# Script to deploy Django messaging app to Kubernetes

set -e  # Exit on error

echo "========================================="
echo "Django Messaging App - Kubernetes Deployment"
echo "========================================="
echo ""

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "ERROR: kubectl is not installed."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed."
    exit 1
fi

# Check if minikube is running (optional, for local development)
if command -v minikube &> /dev/null && minikube status &> /dev/null; then
    echo "Minikube detected. Setting Docker environment..."
    eval $(minikube docker-env)
    echo "✓ Docker environment set for minikube"
    echo ""
fi

# Build Docker image
echo "Building Docker image..."
docker build -t django-messaging-app:latest .
echo "✓ Docker image built successfully"
echo ""

# Apply Kubernetes deployment
echo "Applying Kubernetes deployment..."
kubectl apply -f deployment.yaml
echo "✓ Deployment applied successfully"
echo ""

# Wait for deployment to be ready
echo "Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/django-messaging-app || true
echo ""

# Show deployment status
echo "========================================="
echo "Deployment Status"
echo "========================================="
echo ""
echo "Pods:"
kubectl get pods -l app=django-messaging-app
echo ""

echo "Service:"
kubectl get service django-messaging-app-service
echo ""

echo "Deployment:"
kubectl get deployment django-messaging-app
echo ""

echo "========================================="
echo "Deployment complete!"
echo "========================================="
echo ""
echo "To view logs, run:"
echo "  kubectl logs -l app=django-messaging-app"
echo ""
echo "To get pod name and view specific logs:"
echo "  kubectl get pods"
echo "  kubectl logs <pod-name>"
echo ""
echo "To access the service (if using port-forward):"
echo "  kubectl port-forward service/django-messaging-app-service 8000:8000"
echo ""
