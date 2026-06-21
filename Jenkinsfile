pipeline {
    agent any

    environment {
        GITOPS_DIR = 'gitops-workspace'
        IMAGE_NAME = 'miky97/flask-aws-monitor'
        DOCKERHUB_USERNAME = credentials('dockerhub-username')
        DOCKERHUB_PASSWORD = credentials('dockerhub-password')
        GITOPS_GITHUB_TOKEN = credentials('github-gitops-token')
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/MikyMaor/Docker_K8S_Helm.git'
            }
        }

        stage('Parallel Checks') {
            parallel {
                stage('Linting') {
                    steps {
                        sh '''
                            flake8 app.py || echo "flake8: mock - continuing"
                            hadolint Dockerfile || echo "hadolint: mock - continuing"
                        '''
                    }
                }
                stage('Security Scan') {
                    steps {
                        sh '''
                            bandit -r app.py || echo "bandit: mock - continuing"
                            trivy fs . || echo "trivy: mock - continuing"
                        '''
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} -t ${IMAGE_NAME}:latest ."
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
                    git diff --staged --quiet && exit 0
                    git commit -m "CI: bump image to ${IMAGE_NAME}:${BUILD_NUMBER}"
                    git push origin main
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}
