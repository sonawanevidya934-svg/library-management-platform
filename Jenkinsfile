pipeline {
    agent any

    options {
        timestamps()
    }

    environment {
        PYTHONUNBUFFERED = '1'
        IMAGE_NAME       = 'student-academic-platform'
        IMAGE_TAG        = 'v1.0.0'
    }

    stages {
        stage('SCM Checkout') {
            steps {
                echo 'Checking out source code from GitHub...'
                checkout scm
            }
        }

        stage('Environment Setup') {
            steps {
                echo 'Creating virtual environment and installing dependencies...'
                sh '''
                    python3 --version
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Code Quality - Flake8') {
            steps {
                echo 'Running Flake8 static analysis...'
                sh '''
                    . venv/bin/activate
                    flake8 app database tests run.py
                '''
            }
        }

        stage('Unit & Integration Tests') {
            steps {
                echo 'Running Pytest with coverage and JUnit report...'
                sh '''
                    . venv/bin/activate
                    mkdir -p reports
                    pytest -v --cov=app --cov=database --cov-report=term-missing \
                        --junitxml=reports/test-results.xml tests/
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/test-results.xml'
                }
            }
        }

        stage('Build Docker Image') {
            // Runs automatically once the Dockerfile exists (Topic 5)
            when { expression { fileExists('Dockerfile') } }
            steps {
                echo "Building image ${IMAGE_NAME}:${IMAGE_TAG} ..."
                sh '''
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:build-${BUILD_NUMBER}
                    docker images | grep ${IMAGE_NAME}
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline succeeded for build #${BUILD_NUMBER}."
        }
        failure {
            echo "Build #${BUILD_NUMBER} FAILED - check the console output."
        }
    }
}
