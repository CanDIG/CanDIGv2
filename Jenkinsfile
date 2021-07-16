pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: 'develop']], extensions: [[$class: 'SubmoduleOption', disableSubmodules: false, parentCredentials: false, recursiveSubmodules: true, reference: '', trackingSubmodules: false]], userRemoteConfigs: [[url: 'https://github.com/CanDIG/CanDIGv2']]])
                sh '''bash setup_jenkins.sh'''
            }
        }
        stage('Make') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh '''. $PWD/bin/miniconda3/etc/profile.d/conda.sh; conda activate candig; make images'''
                }
            }
        }
        stage('Publish') {
            steps {
                withCredentials([usernamePassword(credentialsId: '76fcbce2-568d-4fe9-b56e-b269473e7b7f', passwordVariable: 'GITHUB_TOKEN', usernameVariable: 'GITHUB_USER')]) {
                    sh '''. $PWD/bin/miniconda3/etc/profile.d/conda.sh; conda activate candig; echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USER --password-stdin; make docker-push'''
                }
            }
        }
    }
}

