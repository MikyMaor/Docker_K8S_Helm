# Local Jenkins for the final exam CI/CD pipeline

This folder runs Jenkins locally with Docker + Helm support. No AWS required.

## 1. Start Jenkins

```powershell
cd c:\Users\PC\MyApp\FinalExam\Code\jenkins
docker compose up -d --build
```

Open http://localhost:8080

Get the initial admin password:

```powershell
docker exec finalexam-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

## 2. Install suggested plugins

Use the setup wizard defaults (Git, Pipeline, Credentials).

## 3. Add Jenkins credentials

Manage Jenkins → Credentials → Global → Add Credentials

| ID | Type | Value |
|----|------|-------|
| `dockerhub-username` | Secret text | Your Docker Hub username |
| `dockerhub-password` | Secret text | Docker Hub access token |
| `github-gitops-token` | Secret text | GitHub PAT with `repo` scope |

The pipeline uses `github-gitops-token` to push image tag updates to `DevOps-GitOps`.

## 4. Create the pipeline job

1. New Item → Pipeline → name: `flask-aws-monitor`
2. Pipeline script from SCM → Git
3. Repository URL: `https://github.com/MikyMaor/Docker_K8S_Helm.git`
4. Branch: `main`
5. Script path: `Jenkinsfile`

## 5. Run

Build Now → open console output.

Expected flow:

```text
Lint/Security → docker build → docker push → update GitOps repo → git push
```

## 6. Verify

- Docker Hub: image `miky97/flask-aws-monitor:<build-number>`
- GitHub `DevOps-GitOps`: updated `tag` in `flask-aws-monitor/*/values.yaml`
- `rendered/*.yaml` files committed by CI

ArgoCD watches `DevOps-GitOps` and deploys when those files change.
