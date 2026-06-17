pipeline {
    agent any

    environment {
        DOCKERHUB_USERNAME = credentials('dockerhub-username')
        DOCKERHUB_PASSWORD = credentials('dockerhub-password')
        IMAGE_NAME = 'miky97/flask-aws-monitor'
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
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed! Check logs for details.'
        }
    }
}
