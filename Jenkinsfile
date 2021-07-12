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
                sh '''. $PWD/bin/miniconda3/etc/profile.d/conda.sh; conda activate candig; make docker-push'''
            }
        }
    }
}

