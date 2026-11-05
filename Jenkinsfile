
pipeline {
    agent { label 'built-in' }

    environment {
        IMAGE = 'kotharidhruvil/devops-fastapi'
        BUILDKIT_HOST = 'unix:///run/buildkit/buildkitd.sock'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .jenkins-venv
                    .jenkins-venv/bin/python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    .jenkins-venv/bin/python -m pytest -v
                '''
            }
        }

        stage('Build and Push Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'HUB_USER',
                        passwordVariable: 'HUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x
                        export DOCKER_CONFIG="$WORKSPACE/.docker-config"
                        mkdir -p "$DOCKER_CONFIG"
                        chmod 700 "$DOCKER_CONFIG"

                        AUTH=$(printf '%s:%s' "$HUB_USER" "$HUB_TOKEN" | base64 -w0)

                        printf '{"auths":{"https://index.docker.io/v1/":{"auth":"%s"}}}' "$AUTH" \
                          > "$DOCKER_CONFIG/config.json"

                        chmod 600 "$DOCKER_CONFIG/config.json"
                        unset AUTH

                        buildctl \
                          --addr "$BUILDKIT_HOST" \
                          build \
                          --frontend dockerfile.v0 \
                          --local context=. \
                          --local dockerfile=. \
                          --opt platform=linux/amd64 \
                          --output "type=image,name=$IMAGE:$BUILD_NUMBER,push=true"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'FastAPI image successfully pushed to Docker Hub!'
        }

        failure {
            echo 'CI pipeline failed!'
        }

        always {
            sh '''
                rm -rf .jenkins-venv .docker-config
            '''
        }
    }
}
