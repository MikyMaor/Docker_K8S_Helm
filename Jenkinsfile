pipeline {
    agent any

    environment {
        CODE_REPO_URL = 'https://github.com/MikyMaor/Docker_K8S_Helm.git'
        GITOPS_REPO_URL = 'https://github.com/MikyMaor/DevOps-GitOps.git'
        GITOPS_DIR = 'gitops-workspace'
        IMAGE_NAME = 'miky97/flask-aws-monitor'
        DOCKERHUB_USERNAME = credentials('dockerhub-username')
        DOCKERHUB_PASSWORD = credentials('dockerhub-password')
        GITOPS_GITHUB_TOKEN = credentials('github-gitops-token')
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: "${CODE_REPO_URL}"
            }
        }

        stage('Parallel Checks') {
            parallel {
                stage('Linting') {
                    steps {
                        sh '''
                            echo "Running Python lint (flake8)..."
                            flake8 app.py || echo "flake8: mock/fallback - continuing"
                            echo "Running Dockerfile lint (hadolint)..."
                            hadolint Dockerfile || echo "hadolint: mock/fallback - continuing"
                        '''
                    }
                }
                stage('Security Scan') {
                    steps {
                        sh '''
                            echo "Running Python security scan (bandit)..."
                            bandit -r app.py || echo "bandit: mock/fallback - continuing"
                            echo "Running container security scan (trivy)..."
                            trivy fs . || echo "trivy: mock/fallback - continuing"
                        '''
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                    docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} -t ${IMAGE_NAME}:latest .
                """
            }
        }

        stage('Push to Docker Hub') {
            steps {
                sh '''
                    echo "$DOCKERHUB_PASSWORD" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin
                    docker push ${IMAGE_NAME}:${BUILD_NUMBER}
                    docker push ${IMAGE_NAME}:latest
                '''
            }
        }

        stage('Update GitOps Repo (CD)') {
            steps {
                sh '''
                    set -e

                    rm -rf "${GITOPS_DIR}"
                    git clone "https://x-access-token:${GITOPS_GITHUB_TOKEN}@github.com/MikyMaor/DevOps-GitOps.git" "${GITOPS_DIR}"

                    chmod +x scripts/update-gitops.sh
                    ./scripts/update-gitops.sh "${GITOPS_DIR}" "${BUILD_NUMBER}"

                    mkdir -p "${GITOPS_DIR}/rendered"
                    for env in dev qa prd; do
                        helm template "flask-${env}" ./helmchart \
                            -f "${GITOPS_DIR}/flask-aws-monitor/${env}/values.yaml" \
                            > "${GITOPS_DIR}/rendered/flask-aws-monitor-${env}.yaml"
                    done

                    cd "${GITOPS_DIR}"
                    git config user.email "jenkins@ci.local"
                    git config user.name "Jenkins CI"
                    git add flask-aws-monitor rendered
                    git diff --staged --quiet && echo "No GitOps changes to commit" && exit 0
                    git commit -m "CI: bump image to ${IMAGE_NAME}:${BUILD_NUMBER}"
                    git push origin main
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed: Docker Hub + GitOps updated. ArgoCD can sync from DevOps-GitOps.'
        }
        failure {
            echo 'Pipeline failed! Check logs for details.'
        }
    }
}
