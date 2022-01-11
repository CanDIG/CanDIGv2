pipeline {
    agent any
    triggers {
      // Cron job gets executed every day of the working week at 4 p.m  
        cron('00 20 * * 1-5')
    }
    parameters {
      // the choice that the automated system uses is whichever value was last chosen in "Build with Parameters"
      choice choices: ['registry-1.docker.io', 'ghcr.io'], description: 'URL of container registry', name: 'REGISTRY_URL'
    }
    stages {
        stage('Setup') {
            steps {
                sh('echo "REGISTRY_URL is set to ${REGISTRY_URL}"')
                checkout([$class: 'GitSCM', branches: [[name: "$GIT_BRANCH"]], extensions: [[$class: 'SubmoduleOption', disableSubmodules: false, parentCredentials: false, recursiveSubmodules: true, reference: '', trackingSubmodules: false]], userRemoteConfigs: [[url: 'https://github.com/CanDIG/CanDIGv2']]])
                sh '''bash setup_jenkins.sh'''
            }
        }
        stage('Make') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh('. $WORKSPACE/bin/miniconda3/etc/profile.d/conda.sh; conda activate candig; make images OVERRIDE_REGISTRY=${REGISTRY_URL}')
                }
            }
        }
        stage('Publish') {
            steps {
                withCredentials([usernamePassword(credentialsId: params.REGISTRY_URL, passwordVariable: 'TOKEN', usernameVariable: 'USERNAME')]) {
                    sh('. $WORKSPACE/bin/miniconda3/etc/profile.d/conda.sh; conda activate candig; echo ${TOKEN} | docker login ${REGISTRY_URL} -u ${USERNAME} --password-stdin; make docker-push OVERRIDE_REGISTRY=${REGISTRY_URL}')
                }
        stage('Build htsgetapp_server') {
            steps {
                sh '''
                  cd ./lib/htsget-server/htsget_app
                  ls -la
                  bash htsget.sh
                   '''
                }
            }
        }
      post {
  //  Status message gets sent to the Slack Channel after the job finishes
        always {
          success {
            slackSend channel: 'automation-email', message:"Build deployed successfully" -${currentBuild.currentResult} ${env.JOB_NAME} ${env.BUILD_NUMBER} ${env.BUILD_URL}
          }
          failure {
            slackSend channel: 'automation-email', failOnError:true message:"Build failed" -${currentBuild.currentResult} ${env.JOB_NAME} ${env.BUILD_NUMBER} ${env.BUILD_URL}
          }
        }
      }
            }
        }
    }
}

