pipeline {
    agent any
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
                    sh """. ${env.WORKSPACE}/bin/miniconda3/etc/profile.d/conda.sh; conda activate candig; make images REGISTRY=registry-1.docker.io"""
                }
            }
        }
        stage('Publish') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'registry-1.docker.io', passwordVariable: 'GITHUB_TOKEN', usernameVariable: 'GITHUB_USER')]) {
                    sh('. $WORKSPACE/bin/miniconda3/etc/profile.d/conda.sh; conda activate candig; echo $GITHUB_TOKEN | docker login registry-1.docker.io -u $GITHUB_USER --password-stdin; make docker-push REGISTRY=registry-1.docker.io')
                }
            }
        }
    }
}

