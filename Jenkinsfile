// Declarative pipeline for COMP3104 Assignment 2 (Part 3)
// Jenkins prerequisites: plugins "Pipeline", "GitHub", "Docker Pipeline", "SonarQube Scanner";
//   tool "SonarScanner" (Manage Jenkins > Tools), server "sonarqube" (Manage Jenkins > System).
pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'comp3104-assignment2'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
        APP_PORT   = '3000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Unit tests + coverage') {
            steps {
                // Tests run inside a throw-away container: no Python needed on the Jenkins host.
                sh '''
                    docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp \
                      -v "$PWD":/work -w /work python:3.13-slim \
                      sh -c "python -m pip install --user -q coverage && \
                             python -m coverage run -m unittest discover -s tests -t . -v && \
                             python -m coverage xml"
                '''
            }
        }

        stage('SonarQube analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('sonarqube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('Quality gate') {
            steps {
                // Requires the SonarQube webhook -> http://<jenkins>:8080/sonarqube-webhook/
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build image') {
            steps {
                sh 'docker build --build-arg APP_VERSION=${IMAGE_TAG} -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .'
            }
        }

        stage('Scan image (Trivy)') {
            steps {
                // Fail the build on HIGH/CRITICAL findings that already have a fix available.
                sh '''
                    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                      aquasec/trivy:latest image --exit-code 1 --severity HIGH,CRITICAL \
                      --ignore-unfixed --no-progress ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }

        stage('Deploy to VM1') {
            when { branch 'main' }
            steps {
                sh '''
                    docker rm -f ${IMAGE_NAME} || true
                    docker run -d --name ${IMAGE_NAME} --restart unless-stopped \
                      -p ${APP_PORT}:3000 ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }

        stage('Smoke test') {
            when { branch 'main' }
            steps {
                // Deployment is only "done" when the app answers its health check.
                sh '''
                    for i in 1 2 3 4 5 6 7 8 9 10; do
                      if curl -fsS http://localhost:${APP_PORT}/health; then echo; exit 0; fi
                      sleep 3
                    done
                    docker logs ${IMAGE_NAME} || true
                    exit 1
                '''
            }
        }
    }

    post {
        always {
            sh 'docker image prune -f || true'
        }
        failure {
            echo 'Build failed - read the first red stage, then the console log. Do not just re-run.'
        }
    }
}
