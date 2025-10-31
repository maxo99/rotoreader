# rotoreader on Kubernetes

This folder contains Kubernetes manifests to deploy the FastAPI service and schedule periodic collection.

## Files

- `namespace.yaml`: Creates the `rotoreader` namespace.
- `app.yaml`: Deployment and Service for the API (listens on port 8081).
- `ingress.yaml`: Ingress (set your domain and ensure an ingress controller is installed).
- `hpa.yaml`: Horizontal Pod Autoscaler using CPU metrics.
- `collect-cronjob.yaml`: Hourly CronJob that calls `PUT /collect` inside the cluster.

## Apply

```bash
kubectl apply -f k8s/namespace.yaml
kubectl -n rotoreader apply -f k8s/db-config-incluster.yaml    # or k8s/db-config-external.yaml (choose one)
kubectl -n rotoreader apply -f k8s/postgres.yaml                # only if using in-cluster Postgres
kubectl -n rotoreader apply -f k8s/app.yaml -f k8s/hpa.yaml -f k8s/collect-cronjob.yaml -f k8s/ingress.yaml
kubectl -n rotoreader rollout status deploy/rotoreader
```

Notes

- Update the image in `app.yaml` to a versioned tag you push to your registry.
- Ensure Metrics Server and an Ingress controller are installed in your cluster for HPA/Ingress to work.
- Health checks use path `/`, matching the app's health endpoint in `src/rotoreader/app.py`.
- A persistent Postgres is included via `k8s/postgres.yaml` (StatefulSet + PVC). For production, size storage and backups appropriately or use a managed service.
- Choose one DB config:
  - `k8s/db-config-incluster.yaml` → in-cluster Service `postgres:5432`
  - `k8s/db-config-external.yaml` → point to your external host/port

Then apply the manifests as usual:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl -n rotoreader apply -f k8s/app.yaml -f k8s/hpa.yaml -f k8s/collect-cronjob.yaml -f k8s/ingress.yaml
```
