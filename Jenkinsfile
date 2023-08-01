@Library('acv-jenkins-lib')
import com.acvJenkins.*;

pipeline {
    agent {
        kubernetes {
            defaultContainer 'docker'
            yaml new GlobalVars().runnerPod()
        }
    }
    environment {
        NEXUS_CREDS = credentials('NEXUS_CREDS')
        NEXUS_USER = "${NEXUS_CREDS_USR}"
        NEXUS_PASSWORD = "${NEXUS_CREDS_PSW}"
    }
    stages {
        stage('Publish') {
            when {
                expression { env.BRANCH_NAME.endsWith('-acv') }
            }
            steps {
                sh 'make deploy'
            }
        }
    }
    post {
        always {
            sh 'make --ignore-errors stop-ci'
        }
    }
}