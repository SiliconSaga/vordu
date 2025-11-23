String deduceDockerTag() {
    String dockerTag = env.BRANCH_NAME
    if (dockerTag.equals("main") || dockerTag.equals("master")) {
        echo "Building the 'main' branch so we'll publish a Docker tag starting with 'latest'"
        dockerTag = "latest"
    } else {
        dockerTag += "-${env.BUILD_NUMBER}"
        echo "Building a branch other than 'main' so will publish a Docker tag starting with '$dockerTag', not 'latest'"
    }
    return dockerTag
}

pipeline {
    agent {
        label 'docker'
    }
    
    environment {
        GCP_PROJECT_ID = 'teralivekubernetes'
        GCP_REGION = 'us-east1'
        GAR_BASE_URL = "${GCP_REGION}-docker.pkg.dev"
        GAR_REPOSITORY = "vordu"
        DOCKER_TAG = deduceDockerTag()
        FULL_IMAGE_NAME = "${GAR_BASE_URL}/${GCP_PROJECT_ID}/${GAR_REPOSITORY}/vordu:${DOCKER_TAG}"
        K8S_NAMESPACE = 'vordu'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Docker') {
            steps {
                script {
                    withCredentials([file(credentialsId: 'jenkins-gar-sa', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                        sh """
                            # Login to GAR
                            cat \${GOOGLE_APPLICATION_CREDENTIALS} | docker login -u _json_key --password-stdin https://${GAR_BASE_URL}
                            
                            # Build the image
                            docker build -f Dockerfile -t ${FULL_IMAGE_NAME} .
                        """
                    }
                }
            }
        }
        
        stage('Test') {
            agent {
                label 'python-ai'
            }
            steps {
                container('builder') {
                    script {
                        checkout scm
                        sh """
                            # Install dependencies
                            pip install --no-cache-dir -r api/requirements.txt
                            
                            # Start API in background for integration tests
                            export PYTHONPATH=\$PYTHONPATH:.
                            nohup uvicorn api.main:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &
                            
                            # Wait for API to start (health check loop)
                            echo "Waiting for API to start..."
                            for i in {1..30}; do
                                if curl -s http://localhost:8000/docs > /dev/null; then
                                    echo "API is up!"
                                    break
                                fi
                                echo "Waiting for API... (\$i/30)"
                                sleep 1
                            done
                            
                            # Check if API actually started
                            if ! curl -s http://localhost:8000/docs > /dev/null; then
                                echo "API failed to start. Logs:"
                                cat /tmp/api.log
                                exit 1
                            fi
                            
                            # Run tests (generating cucumber.json)
                            pytest || true
                        """
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'cucumber.json', allowEmptyArchive: true
                    stash includes: 'cucumber.json', name: 'test-results', allowEmpty: true
                }
            }
        }
        
        stage('Push Docker') {
            steps {
                script {
                    withCredentials([file(credentialsId: 'jenkins-gar-sa', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                        sh """
                            cat \${GOOGLE_APPLICATION_CREDENTIALS} | docker login -u _json_key --password-stdin https://${GAR_BASE_URL}
                            docker push ${FULL_IMAGE_NAME}
                        """
                    }
                }
            }
        }
        
        stage('k8s deploy') {
            agent {
                label 'kubectl'
            }
            steps {
                container('utility') {
                    withKubeConfig(credentialsId: 'utility-admin-kubeconfig-sa-token') {
                        script {
                            // Ensure namespace exists
                            sh """
                                kubectl get ns ${K8S_NAMESPACE} || kubectl create ns ${K8S_NAMESPACE}
                            """
                            
                            // Update deployment YAML with actual image name
                            sh """
                                sed -i 's|us-east1-docker.pkg.dev/teralivekubernetes/vordu/vordu:latest|${FULL_IMAGE_NAME}|g' k8s/deployment.yaml
                            """
                            
                            // Deploy Resources
                            sh """
                                kubectl apply -f k8s/pvc.yaml -n ${K8S_NAMESPACE}
                                kubectl apply -f k8s/deployment.yaml -n ${K8S_NAMESPACE}
                                kubectl apply -f k8s/service.yaml -n ${K8S_NAMESPACE}
                                kubectl apply -f k8s/ingress.yaml -n ${K8S_NAMESPACE}
                            """

                            // Force restart to get "latest"
                            sh """
                                kubectl rollout restart deployment/vordu -n ${K8S_NAMESPACE}
                            """
                            
                            // Wait for rollout to complete before ingestion
                            sh """
                                kubectl rollout status deployment/vordu -n ${K8S_NAMESPACE} --timeout=60s || true
                            """
                        }
                    }
                }
            }
        }

        stage('Ingest BDD') {
            agent {
                label 'python-ai'
            }
            steps {
                container('builder') {
                    script {
                        checkout scm
                        unstash 'test-results'
                        
                        // Ingest the test results into the deployed API
                        sh """
                            # Install requests if not present
                            pip install requests
                            
                            # Run ingestion script
                            python scripts/ingest_cucumber.py cucumber.json http://vordu-service.${K8S_NAMESPACE}.svc.cluster.local
                        """
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo "Deployment successful! Vörðu available at https://vordu.siliconsaga.org"
        }
        failure {
            echo "Deployment failed. Check logs: kubectl logs -l app=vordu -n ${env.K8S_NAMESPACE}"
        }
    }
}
