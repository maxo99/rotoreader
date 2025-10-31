
set shell := ["bash", "-cu"]

# Defaults
image := "maxo5499/sportsstack-rotoreader:latest"
cluster := "rotoreader"
ns := "rotoreader"

# Kubernetes: local Kind cluster
cluster-up:
	bash scripts/kind-create-cluster.sh {{cluster}}

cluster-down:
	kind delete cluster --name {{cluster}}

image-build:
	./build.sh

kind-load:
	kind load docker-image {{image}} --name {{cluster}}

# Apply manifests (choose one of these)
k8s-apply-incluster:
	kubectl apply -f k8s/namespace.yaml
	kubectl -n {{ns}} apply -f k8s/db-config-incluster.yaml
	kubectl -n {{ns}} apply -f k8s/postgres.yaml
	kubectl -n {{ns}} apply -f k8s/app.yaml -f k8s/hpa.yaml -f k8s/collect-cronjob.yaml -f k8s/ingress.yaml
	kubectl -n {{ns}} rollout status deploy/rotoreader

k8s-apply-external:
	kubectl apply -f k8s/namespace.yaml
	kubectl -n {{ns}} apply -f k8s/db-config-external.yaml
	kubectl -n {{ns}} apply -f k8s/app.yaml -f k8s/hpa.yaml -f k8s/collect-cronjob.yaml -f k8s/ingress.yaml
	kubectl -n {{ns}} rollout status deploy/rotoreader

# Operate app
k8s-restart:
	kubectl -n {{ns}} rollout restart deploy/rotoreader
	kubectl -n {{ns}} rollout status deploy/rotoreader

k8s-logs:
	kubectl -n {{ns}} logs deploy/rotoreader -c api --tail=200 -f

pf-svc:
	kubectl -n {{ns}} port-forward svc/rotoreader 8081:8081

pf-ingress:
	kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8080:80

# Database helpers
db-shell:
	kubectl -n {{ns}} exec -it svc/postgres -- psql -U postgres -d rotoreader

clear_db:
	docker compose exec -T postgres psql -U postgres -d rotoreader -c "DROP TABLE IF EXISTS teamdata CASCADE; DROP TABLE IF EXISTS feeddata CASCADE;"