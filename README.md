# DevOps SRE Demo

A minimal Flask application packaged for containerized deployment with Kubernetes.

## Requirements

- Python 3.11+ (or a supported Python 3 runtime)
- Docker (for container builds)
- kubectl (for Kubernetes manifests)

## Setup

1. Create the virtual environment:
   ```powershell
   python -m venv .venv
   ```

2. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Run locally

```powershell
python app.py
```

Then open `http://127.0.0.1:8080` in your browser.

## Docker

Build the image:
```powershell
docker build -t devops-sre-demo:latest .
```

Run the container:
```powershell
docker run -p 8080:8080 devops-sre-demo:latest
```

## Kubernetes

Apply the manifests:
```powershell
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Check the service and deployment status with:
```powershell
kubectl get deployments,services
```
