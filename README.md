# 🚀 Flask AWS Monitor (Docker + Kubernetes + Helm)

## Final exam status (local workspace)

| Component | Status |
|-----------|--------|
| `app.py` — AWS boto3 monitor (VPC/LB/AMI bug fixed) | ✅ Done |
| `requirements.txt` — flask + boto3 | ✅ Done |
| `Dockerfile` | ✅ Done (single-stage) |
| `Jenkinsfile` — parallel lint/security + build/push | ✅ Done (update repo URL if using new repo) |
| `helmchart/` | ✅ Done |
| Azure DevOps pipeline YAML | ❌ Not yet (bonus) |
| Git Flow branches (`dev`, feature branches) | ❌ You need to create on GitHub |
| Push to Docker Hub + screenshots | ❌ Run manually |
| ArgoCD GitOps repo | 📁 Created locally under `../GitOps` — push to new GitHub repo |

---

A small Flask app that lists AWS resources (EC2, VPCs, Load Balancers, AMIs) and supports a full DevOps flow:

- 🐳 Build a Docker image
- ☸️ Deploy to Kubernetes using Helm
- 🔁 Upgrade / rollback releases

The app exposes:

- 🌐 `GET /` – AWS resources tables (EC2, VPCs, Load Balancers, AMIs)
- 🩺 `GET /healthz` – health endpoint used by Kubernetes probes

> Port: **5001**

---

## ✅ What you will deliver (assignment-style)

- 📦 A Helm chart under `helmchart/`
- ⚙️ A `values.yaml` that makes the deployment configurable
- 📸 Screenshots / logs proving:
  - successful install/upgrade
  - pods/services are running
  - you can access the app
  - upgrade + rollback works

---

## 🧰 Prerequisites

- 🐳 Docker (Docker Desktop is fine)
- ☸️ A Kubernetes cluster (local is fine: Docker Desktop / kind / minikube)
- 🧱 `kubectl`
- 🎛️ `helm`

Quick checks:

```bash
kubectl version --client
helm version
kubectl get nodes
```

---

## 🧠 Project structure

```text
K8S_Project/
├─ app.py                    # Flask application (GUI + health + status)
├─ requirements.txt          # Python dependencies
├─ Dockerfile                # Builds the image that runs app.py
├─ helmchart/                # Helm chart (Deployment/Service/Ingress templates + values)
└─ apps/                     # Reserved folder (course repo structure requirement)
```

---

## 🧩 What each Kubernetes/Helm resource does

- 📄 **Deployment** (`helmchart/templates/deployment.yaml`)
  - Runs your container(s)
  - Controls replicas (scaling)
  - Defines env vars (AWS keys)
  - Defines health probes (`/healthz`)
  - Applies CPU/memory requests/limits

- 🌐 **Service** (`helmchart/templates/service.yaml`)
  - Gives a stable virtual IP/DNS for the Pods
  - Exposes port **5001** inside the cluster
  - Can be configured as `ClusterIP` / `LoadBalancer` via `values.yaml`

- 🧭 **Ingress** (optional bonus) (`helmchart/templates/ingress.yaml`)
  - Routes HTTP traffic by host/path to your Service
  - Disabled by default (`ingress.enabled: false`)

---

## 🌳 Process tree (end-to-end)

```text
Build image 🐳
  └─ Push image to Docker Hub ☁️
       └─ Configure Helm values ⚙️
            └─ Install/Upgrade with Helm 🎛️
                 └─ Verify pods/services ☸️
                      └─ Access the app 🌐
                           └─ Upgrade & rollback 🔁
```

---

## 1) 🐳 Build & push the Docker image

From the repo root:

```bash
cd /Users/mike/K8S_Project
docker login
docker build -t <DOCKERHUB_USER>/flask-aws-monitor:latest .
docker push <DOCKERHUB_USER>/flask-aws-monitor:latest
```

---

## 2) ⚙️ Configure Helm values (image + secrets + exposure)

### 2.1 Set your Docker Hub image

Edit `helmchart/values.yaml`:

- `image.repository: <DOCKERHUB_USER>/flask-aws-monitor`
- `image.tag: latest`
- `image.pullPolicy: Always` (pull latest)

### 2.2 AWS keys (recommended: keep out of git)

Create `helmchart/values.secrets.yaml` (this file is **gitignored**):

```yaml
aws:
  accessKey: "AKIA..."
  secretKey: "..."
```

### 2.3 Service exposure

For local clusters, keep:

```yaml
service:
  type: ClusterIP
  port: 5001
```

---

## 3) 🎛️ Deploy with Helm

```bash
kubectl get nodes

helm lint ./helmchart

helm upgrade --install flask-monitor ./helmchart \
  -f helmchart/values.yaml \
  -f helmchart/values.secrets.yaml

kubectl get pods,svc
```

---

## 4) 🔍 Verify health “for real”

### 4.1 Watch the rollout

```bash
kubectl rollout status deploy/flask-monitor-flask-aws-monitor
kubectl get pods -o wide
```

### 4.2 Check logs

```bash
kubectl logs deploy/flask-monitor-flask-aws-monitor --tail=100
```

### 4.3 Validate in-cluster health endpoint

```bash
kubectl exec -it deploy/flask-monitor-flask-aws-monitor -- wget -qO- http://127.0.0.1:5001/healthz
```

Expected: `ok`

---

## 5) 🌐 Access the app (local cluster)

Because local clusters often don’t provide a real `EXTERNAL-IP`, use port-forward:

```bash
kubectl port-forward svc/flask-monitor-flask-aws-monitor 5001:5001
```

Open:

- `http://127.0.0.1:5001/` (GUI)
- `http://127.0.0.1:5001/healthz`
- `http://127.0.0.1:5001/api/status`

Terminal checks:

```bash
curl -sS http://127.0.0.1:5001/healthz
curl -sS http://127.0.0.1:5001/api/status
```

---

## 6) 🔁 Upgrade & rollback (required)

```bash
helm history flask-monitor

# Example upgrade: scale to 2 replicas
helm upgrade flask-monitor ./helmchart --set replicaCount=2
kubectl get pods

# Roll back to revision 1
helm rollback flask-monitor 1
kubectl get pods
```

---

## 🧹 Cleanup (optional)

```bash
helm uninstall flask-monitor
kubectl get pods,svc
```


