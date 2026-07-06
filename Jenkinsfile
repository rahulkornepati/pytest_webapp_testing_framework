pipeline {
    agent any

    options {
        timestamps()
        ansiColor('xterm')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    parameters {
        choice(name: 'BROWSER', choices: ['chrome', 'firefox', 'edge'], description: 'Browser for Selenium execution')
        choice(name: 'MARKERS', choices: ['smoke', 'regression', 'login', 'cart', 'checkout', 'inventory'], description: 'Pytest marker suite')
        booleanParam(name: 'HEADLESS', defaultValue: true, description: 'Run browser in headless mode')
        string(name: 'BASE_URL', defaultValue: 'https://www.saucedemo.com/', description: 'Application URL')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Selenium Tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    export PYTEST_REPORT_RUN_ID="${BUILD_TAG:-jenkins}_${BUILD_NUMBER:-local}"
                    HEADLESS_FLAG=""
                    if [ "${HEADLESS}" = "true" ]; then
                      HEADLESS_FLAG="--headless"
                    fi
                    python run_tests.py --browser "${BROWSER}" --markers "${MARKERS}" --base-url "${BASE_URL}" ${HEADLESS_FLAG}
                '''
            }
        }
    }

    post {
        always {
            publishHTML(target: [
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: '**/report.html',
                reportName: 'Pytest HTML Report'
            ])
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
            junit allowEmptyResults: true, testResults: 'reports/**/junit.xml'
        }
    }
}
