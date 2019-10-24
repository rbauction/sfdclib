pipeline {
    agent any
    environment {
        ARTIFACTORY_CREDS = credentials('ARTIFACTORY_CREDS')
        ARTIFACTORY_USER = "${ARTIFACTORY_CREDS_USR}"
        ARTIFACTORY_PASSWORD = "${ARTIFACTORY_CREDS_PSW}"
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