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
        string(name: 'API_BASE_URL', defaultValue: 'https://api.escuelajs.co/api/v1', description: 'API base URL')
        choice(name: 'API_AUTH', choices: ['token', 'api-key', 'credentials'], description: 'API authentication method')
        choice(name: 'TEST_SUITE', choices: ['all', 'ui', 'api'], description: 'Test suite to run')
    }

    environment {
        API_BASE_URL = "${params.API_BASE_URL}"
        API_USERNAME = 'john@mail.com'
        API_PASSWORD = 'changeme'
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

        stage('Run Tests') {
            parallel {
                stage('UI — Selenium Tests') {
                    when {
                        expression { params.TEST_SUITE in ['all', 'ui'] }
                    }
                    steps {
                        sh '''
                            . .venv/bin/activate
                            export PYTEST_REPORT_RUN_ID="${BUILD_TAG:-jenkins}_${BUILD_NUMBER:-local}_ui"
                            HEADLESS_FLAG=""
                            if [ "${HEADLESS}" = "true" ]; then
                              HEADLESS_FLAG="--headless"
                            fi
                            python run_tests.py --browser "${BROWSER}" --markers "${MARKERS}" --base-url "${BASE_URL}" ${HEADLESS_FLAG}
                        '''
                    }
                }

                stage('API — Integration Tests') {
                    when {
                        expression { params.TEST_SUITE in ['all', 'api'] }
                    }
                    steps {
                        sh '''
                            . .venv/bin/activate
                            export PYTEST_REPORT_RUN_ID="${BUILD_TAG:-jenkins}_${BUILD_NUMBER:-local}_api"
                            export API_BASE_URL="${API_BASE_URL}"
                            python -m pytest api_tests/ \
                                --html=reports/api_report.html --self-contained-html \
                                --junitxml=reports/api_junit.xml \
                                -m "api" \
                                --report-run-id "${PYTEST_REPORT_RUN_ID}"
                        '''
                    }
                }
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
