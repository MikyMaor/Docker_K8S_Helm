# Flask AWS Monitor

Flask app that lists AWS EC2, VPCs, Load Balancers, and AMIs. Packaged with Docker, Helm, and Jenkins CI/CD.

**Endpoints:** `GET /` · `GET /healthz` · port **5001**

## Structure

```
app.py
Dockerfile              # Flask application image
Jenkinsfile             # CI: build, push, update GitOps
helmchart/              # Kubernetes Helm chart
jenkins/                # Local Jenkins (docker compose)
scripts/                # CI helper scripts
apps/                   # Reserved (course layout)
```

## Docker

```bash
docker build -t miky97/flask-aws-monitor:latest .
docker run -p 5001:5001 \
  -e AWS_ACCESS_KEY_ID=... \
  -e AWS_SECRET_ACCESS_KEY=... \
  miky97/flask-aws-monitor:latest
```

## Helm

```bash
cp helmchart/values.secrets.yaml.example helmchart/values.secrets.yaml
# edit AWS keys in values.secrets.yaml

helm upgrade --install flask-monitor ./helmchart \
  -f helmchart/values.yaml \
  -f helmchart/values.secrets.yaml

kubectl port-forward svc/flask-monitor-flask-aws-monitor 5001:5001
```

## Jenkins

See `jenkins/README.md`. Pipeline pushes to Docker Hub and updates the GitOps repo (`DevOps-GitOps`).
