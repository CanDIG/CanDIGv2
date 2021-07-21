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
                    sh """. ${env.WORKSPACE}/bin/miniconda3/etc/profile.d/conda.sh; conda activate candig; make images"""
                }
            }
        }
        stage('Publish') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'registry-1.docker.io', passwordVariable: 'TOKEN', usernameVariable: 'USERNAME')]) {
                    sh('. $WORKSPACE/bin/miniconda3/etc/profile.d/conda.sh; conda activate candig; echo $TOKEN | docker login registry-1.docker.io -u $USERNAME --password-stdin; make docker-push')
                }
            }
        }
    }
}

