# Local Jenkins

Runs Jenkins with Docker and Helm for the CI pipeline.

```powershell
docker compose up -d --build
```

UI: http://localhost:8080

**Credentials** (Manage Jenkins → Credentials → Secret text):

| ID | Value |
|----|-------|
| `dockerhub-username` | Docker Hub username |
| `dockerhub-password` | Docker Hub access token |
| `github-gitops-token` | GitHub PAT (`repo` scope) |

**Pipeline job:** Pipeline from SCM → `https://github.com/MikyMaor/Docker_K8S_Helm.git` → branch `main` → script `Jenkinsfile`

`jenkins/Dockerfile` builds the Jenkins image (not the Flask app — see root `Dockerfile`).
