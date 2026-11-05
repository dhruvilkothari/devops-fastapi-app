
pipeline {
    agent { label 'built-in' }

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
        stage('test'){
            steps {
                sh '''
                cd ../
                pwd
                ls -la
                '''
            }
        }
    }

    post {
        success {
            echo 'FastAPI CI pipeline passed!'
        }

        failure {
            echo 'FastAPI CI pipeline failed!'
        }

        always {
            sh 'rm -rf .jenkins-venv'
        }
    }
}
