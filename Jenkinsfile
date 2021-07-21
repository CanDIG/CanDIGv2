pipeline {
    agent any
    parameters {
      string defaultValue: 'registry-1.docker.io', name: 'CONTAINER_REGISTRY', description: 'The URL of the registry to push images to'
      credentials credentialType: 'com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl', defaultValue: 'registry-1.docker.io', name: 'REGISTRY', required: false
    }
    stages {
        stage('Setup') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: "${env.GIT_BRANCH}"]], extensions: [[$class: 'SubmoduleOption', disableSubmodules: false, parentCredentials: false, recursiveSubmodules: true, reference: '', trackingSubmodules: false]], userRemoteConfigs: [[url: 'https://github.com/CanDIG/CanDIGv2']]])
                sh '''bash setup_jenkins.sh'''
            }
        }
        stage('Make') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh """. ${env.WORKSPACE}/bin/miniconda3/etc/profile.d/conda.sh; conda activate candig; make images REGISTRY=${params.CONTAINER_REGISTRY}"""
                }
            }
        }
        stage('Publish') {
            steps {
                sh 'echo "SSH private key is located at $REGISTRY_CREDS"'
                sh """. ${env.WORKSPACE}/bin/miniconda3/etc/profile.d/conda.sh; conda activate candig; echo $REGISTRY_PSW | docker login ${params.CONTAINER_REGISTRY} -u $REGISTRY_USR --password-stdin; make docker-push REGISTRY=${params.CONTAINER_REGISTRY}"""
            }
        }
    }
}

