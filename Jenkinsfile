
pipeline {
    agent { label 'built-in' }

    environment {
        IMAGE = 'kotharidhruvil/devops-fastapi'
        BUILDKIT_HOST = 'unix:///run/buildkit/buildkitd.sock'
        GITOPS_REPO = 'https://github.com/dhruvilkothari/devops-gitops.git'
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
                    set -eu
                    python3 -m venv .jenkins-venv
                    .jenkins-venv/bin/python -m pip install -r requirements.txt
                    .jenkins-venv/bin/python -m pip install PyYAML
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    set -eu
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
                        set -eu
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

        stage('Update GitOps Repository') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'github-gitops-creds',
                        usernameVariable: 'GIT_USER',
                        passwordVariable: 'GIT_TOKEN'
                    )
                ]) {
                    sh '''
                        set -eu
                        set +x

                        export GIT_TERMINAL_PROMPT=0

                        # Create Git authentication helper.
                        printf '%s\\n' \
                          '#!/bin/sh' \
                          'case "$1" in' \
                          '  *Username*) printf "%s\\\\n" "$GIT_USER" ;;' \
                          '  *Password*) printf "%s\\\\n" "$GIT_TOKEN" ;;' \
                          '  *) exit 1 ;;' \
                          'esac' \
                          > "$WORKSPACE/.git-askpass"

                        chmod 700 "$WORKSPACE/.git-askpass"
                        export GIT_ASKPASS="$WORKSPACE/.git-askpass"

                        # Clone the GitOps repository.
                        rm -rf "$WORKSPACE/gitops-repo"

                        git clone \
                          "$GITOPS_REPO" \
                          "$WORKSPACE/gitops-repo"

                        # Update the Helm image tag.
                        .jenkins-venv/bin/python scripts/update_gitops_tag.py \
                          "$WORKSPACE/gitops-repo/charts/devops-fastapi/values.yaml" \
                          "$BUILD_NUMBER"

                        cd "$WORKSPACE/gitops-repo"

                        git config user.name "Jenkins CI"
                        git config user.email "jenkins@localhost"

                        git add charts/devops-fastapi/values.yaml

                        # Commit only when the image tag changed.
                        if git diff --cached --quiet; then
                            echo "GitOps image tag already up to date"
                        else
                            git commit -m "Update FastAPI image to build $BUILD_NUMBER"
                            git push origin HEAD:main
                        fi
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'CI successful! Docker image pushed and GitOps repository updated.'
        }

        failure {
            echo 'CI/CD pipeline failed. Check the Jenkins console output.'
        }

        always {
            sh '''
                rm -rf .jenkins-venv .docker-config .git-askpass gitops-repo
            '''
        }
    }
}
