pipeline {

    agent any

    parameters {

        choice(
            name: 'ENVIRONMENT',
            choices: ['DEV', 'UAT', 'PRODUCTION'],
            description: 'Select deployment environment'
        )

        choice(
            name: 'ACTION',
            choices: ['DEPLOY', 'ROLLBACK'],
            description: 'Select deployment action'
        )

        string(
            name: 'VERSION',
            defaultValue: '5.0',
            description: 'Application version'
        )

        choice(
            name: 'RUN_TESTS',
            choices: ['YES', 'NO'],
            description: 'Run automated tests'
        )

        choice(
            name: 'CONFIRM_PRODUCTION',
            choices: ['NO', 'YES'],
            description: 'Required YES for production deployment'
        )
    }

    environment {

        DOCKER = 'C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        COMPOSE = 'C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker-compose.exe'

        IMAGE_REPO = 'customer-app'
    }

    stages {

        // =========================================================
        // 1. RESOLVE ENVIRONMENT
        // =========================================================

        stage('Resolve Environment') {

            steps {

                script {

                    if (params.ENVIRONMENT == 'DEV') {

                        env.TARGET_BRANCH = 'develop'
                        env.APP_CONTAINER = 'customer-app-dev'
                        env.DB_CONTAINER = 'customer-db-dev'
                        env.HOST_PORT = '8081'
                        env.NETWORK_NAME = 'customer-dev-net'
                        env.DB_VOLUME = 'customer-db-dev-data'
                        env.COMPOSE_PROJECT = 'customer-dev'
                        env.DB_HOST = 'customer-db-dev'
                        env.DB_NAME = 'customer_db'
                        env.DB_USER = 'customer_user'
                        env.DB_PASSWORD = 'dev_password'
                        env.DB_ROOT_PASSWORD = 'dev_root_password'
                        env.ENV_NAME = 'DEV'

                    }
                    else if (params.ENVIRONMENT == 'UAT') {

                        env.TARGET_BRANCH = 'release'
                        env.APP_CONTAINER = 'customer-app-uat'
                        env.DB_CONTAINER = 'customer-db-uat'
                        env.HOST_PORT = '8082'
                        env.NETWORK_NAME = 'customer-uat-net'
                        env.DB_VOLUME = 'customer-db-uat-data'
                        env.COMPOSE_PROJECT = 'customer-uat'
                        env.DB_HOST = 'customer-db-uat'
                        env.DB_NAME = 'customer_db'
                        env.DB_USER = 'customer_user'
                        env.DB_PASSWORD = 'uat_password'
                        env.DB_ROOT_PASSWORD = 'uat_root_password'
                        env.ENV_NAME = 'UAT'

                    }
                    else if (params.ENVIRONMENT == 'PRODUCTION') {

                        env.TARGET_BRANCH = 'main'
                        env.APP_CONTAINER = 'customer-app-prod'
                        env.DB_CONTAINER = 'customer-db-prod'
                        env.HOST_PORT = '8083'
                        env.NETWORK_NAME = 'customer-prod-net'
                        env.DB_VOLUME = 'customer-db-prod-data'
                        env.COMPOSE_PROJECT = 'customer-prod'
                        env.DB_HOST = 'customer-db-prod'
                        env.DB_NAME = 'customer_db'
                        env.DB_USER = 'customer_user'
                        env.DB_PASSWORD = 'prod_password'
                        env.DB_ROOT_PASSWORD = 'prod_root_password'
                        env.ENV_NAME = 'PRODUCTION'

                    }
                    else {

                        error('Invalid environment selected.')

                    }

                    env.IMAGE_NAME = "${env.IMAGE_REPO}:${params.VERSION}"

                    echo """
============================================================
RESOLVED DEPLOYMENT CONFIGURATION
============================================================

ENVIRONMENT       : ${env.ENV_NAME}
BRANCH            : ${env.TARGET_BRANCH}
ACTION            : ${params.ACTION}
VERSION           : ${params.VERSION}

IMAGE             : ${env.IMAGE_NAME}

APP CONTAINER     : ${env.APP_CONTAINER}
DATABASE          : ${env.DB_CONTAINER}

HOST PORT         : ${env.HOST_PORT}
NETWORK           : ${env.NETWORK_NAME}
DB VOLUME         : ${env.DB_VOLUME}

DB HOST           : ${env.DB_HOST}
DB NAME           : ${env.DB_NAME}
DB USER           : ${env.DB_USER}

COMPOSE PROJECT   : ${env.COMPOSE_PROJECT}

============================================================
"""

                    // Production confirmation
                    if (
                        params.ENVIRONMENT == 'PRODUCTION' &&
                        params.CONFIRM_PRODUCTION != 'YES'
                    ) {

                        error(
                            'PRODUCTION deployment requires CONFIRM_PRODUCTION = YES'
                        )
                    }

                    // Prevent invalid production combinations
                    if (
                        params.ENVIRONMENT == 'PRODUCTION' &&
                        env.TARGET_BRANCH != 'main'
                    ) {

                        error(
                            'Invalid production configuration. Production must use main branch.'
                        )
                    }

                    // Branch mapping validation
                    if (
                        params.ENVIRONMENT == 'DEV' &&
                        env.TARGET_BRANCH != 'develop'
                    ) {

                        error(
                            'Invalid DEV configuration. DEV must use develop branch.'
                        )
                    }

                    if (
                        params.ENVIRONMENT == 'UAT' &&
                        env.TARGET_BRANCH != 'release'
                    ) {

                        error(
                            'Invalid UAT configuration. UAT must use release branch.'
                        )
                    }
                }
            }
        }


        // =========================================================
        // 2. CHECKOUT SELECTED BRANCH
        // =========================================================

        stage('Checkout Selected Branch') {

            steps {

                echo "Checking out branch: ${env.TARGET_BRANCH}"

                bat """
                    git fetch --all --prune
                    git checkout ${env.TARGET_BRANCH}
                    git reset --hard origin/${env.TARGET_BRANCH}
                    git clean -fd
                """

                bat """
                    echo.
                    echo ===== CURRENT GIT COMMIT =====
                    git log -1 --oneline
                    echo.
                    echo ===== CURRENT BRANCH =====
                    git branch --show-current
                """
            }
        }


        // =========================================================
        // 3. RUN TESTS
        // =========================================================

        stage('Run Tests') {

            when {
                expression {
                    params.RUN_TESTS == 'YES'
                }
            }

            steps {

                echo "Running automated tests..."

               bat """
    "${DOCKER}" run --rm ^
        -v "%WORKSPACE%:/workspace" ^
        -w /workspace ^
        python:3.12-slim ^
        sh -c "pip install -q -r app/requirements.txt && pytest tests -v"
"""
            }
        }


        // =========================================================
        // 4. BUILD DOCKER IMAGE
        // =========================================================

        stage('Build Docker Image') {

            steps {

                echo "Building Docker image ${env.IMAGE_NAME}"

                bat """
                    "${DOCKER}" build ^
                    -t ${env.IMAGE_NAME} ^
                    .
                """

                bat """
                    echo.
                    echo ===== DOCKER IMAGE =====
                    "${DOCKER}" image inspect ${env.IMAGE_NAME}
                """
            }
        }


        // =========================================================
        // 5. CREATE ENVIRONMENT CONFIG
        // =========================================================

        stage('Create Environment Configuration') {

            steps {

                script {

                    writeFile(
                        file: '.env',
                        text: """
IMAGE_NAME=${env.IMAGE_NAME}
APP_CONTAINER=${env.APP_CONTAINER}
DB_CONTAINER=${env.DB_CONTAINER}
DB_HOST=${env.DB_HOST}
HOST_PORT=${env.HOST_PORT}
NETWORK_NAME=${env.NETWORK_NAME}
DB_VOLUME=${env.DB_VOLUME}
APP_VERSION=${params.VERSION}
ENVIRONMENT=${env.ENV_NAME}
DB_NAME=${env.DB_NAME}
DB_USER=${env.DB_USER}
DB_PASSWORD=${env.DB_PASSWORD}
DB_ROOT_PASSWORD=${env.DB_ROOT_PASSWORD}
"""
                    )
                }

                bat """
                    echo ===== ENVIRONMENT CONFIG CREATED =====
                    type .env
                """
            }
        }


        // =========================================================
        // 6. DEPLOY
        // =========================================================

        stage('Deploy Application') {

            when {
                expression {
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {

                echo "Deploying ${env.ENV_NAME}"

                bat """
                    echo.
                    echo ===== STOPPING OLD APPLICATION =====
                    "${COMPOSE}" -p ${env.COMPOSE_PROJECT} down
                """

                bat """
                    echo.
                    echo ===== STARTING APPLICATION AND DATABASE =====
                    "${COMPOSE}" -p ${env.COMPOSE_PROJECT} up -d
                """

                echo "Waiting for containers to start..."

                bat """
                    ping 127.0.0.1 -n 21 >nul
                """

                bat """
                    echo.
                    echo ===== DOCKER PS =====
                    "${DOCKER}" ps -a
                """
            }
        }


        // =========================================================
        // 7. ROLLBACK
        // =========================================================

        stage('Rollback Application') {

            when {
                expression {
                    params.ACTION == 'ROLLBACK'
                }
            }

            steps {

                echo "Starting rollback to version ${params.VERSION}"

                bat """
                    echo.
                    echo ===== CHECKING ROLLBACK IMAGE =====
                    "${DOCKER}" image inspect ${env.IMAGE_NAME}
                """

                bat """
                    echo.
                    echo ===== STOPPING CURRENT DEPLOYMENT =====
                    "${COMPOSE}" -p ${env.COMPOSE_PROJECT} down
                """

                bat """
                    echo.
                    echo ===== STARTING ROLLBACK VERSION =====
                    "${COMPOSE}" -p ${env.COMPOSE_PROJECT} up -d
                """

                echo "Waiting for rollback containers..."

                bat """
                    ping 127.0.0.1 -n 21 >nul
                """
            }
        }


        // =========================================================
        // 8. CONTAINER VALIDATION
        // =========================================================

        stage('Validate Containers') {

            steps {

                echo "Validating application and database containers..."

                bat """
                    echo.
                    echo ===== APPLICATION CONTAINER =====
                    "${DOCKER}" inspect ${env.APP_CONTAINER}

                    echo.
                    echo ===== DATABASE CONTAINER =====
                    "${DOCKER}" inspect ${env.DB_CONTAINER}
                """

                bat """
                    echo.
                    echo ===== RUNNING CONTAINERS =====
                    "${DOCKER}" ps --format "table {{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}"
                """

                bat """
                    echo.
                    echo ===== CHECK APPLICATION STATUS =====
                    "${DOCKER}" inspect -f "{{.State.Status}}" ${env.APP_CONTAINER}
                """

                bat """
                    echo.
                    echo ===== CHECK DATABASE STATUS =====
                    "${DOCKER}" inspect -f "{{.State.Status}}" ${env.DB_CONTAINER}
                """
            }
        }


        // =========================================================
        // 9. NETWORK VALIDATION
        // =========================================================

        stage('Validate Docker Network') {

            steps {

                echo "Checking Docker network ${env.NETWORK_NAME}"

                bat """
                    echo.
                    echo ===== NETWORK INSPECT =====
                    "${DOCKER}" network inspect ${env.NETWORK_NAME}
                """

                bat """
                    echo.
                    echo ===== APPLICATION NETWORKS =====
                    "${DOCKER}" inspect -f "{{json .NetworkSettings.Networks}}" ${env.APP_CONTAINER}
                """

                bat """
                    echo.
                    echo ===== DATABASE NETWORKS =====
                    "${DOCKER}" inspect -f "{{json .NetworkSettings.Networks}}" ${env.DB_CONTAINER}
                """
            }
        }


        // =========================================================
        // 10. VOLUME VALIDATION
        // =========================================================

        stage('Validate Database Volume') {

            steps {

                echo "Checking database volume ${env.DB_VOLUME}"

                bat """
                    echo.
                    echo ===== DATABASE VOLUME =====
                    "${DOCKER}" volume inspect ${env.DB_VOLUME}
                """
            }
        }


        // =========================================================
        // 11. HEALTH CHECK
        // =========================================================

        stage('Health Check') {

            steps {

                echo "Checking application health..."

                bat """
                    echo.
                    echo ===== APPLICATION HEALTH =====

                    curl.exe --fail ^
                    http://localhost:${env.HOST_PORT}/health
                """
            }
        }


        // =========================================================
        // 12. APP TO DATABASE CONNECTIVITY
        // =========================================================

        stage('Validate App To Database') {

            steps {

                echo "Testing application container -> database container connectivity..."

                bat """
                    echo.
                    echo ===== APP TO DATABASE TEST =====

                    "${DOCKER}" exec ^
                    ${env.APP_CONTAINER} ^
                    python -c "import os,mysql.connector; c=mysql.connector.connect(host=os.environ['DB_HOST'],user=os.environ['DB_USER'],password=os.environ['DB_PASSWORD'],database=os.environ['DB_NAME']); print('APP_TO_DB_CONNECTION_SUCCESS'); c.close()"
                """
            }
        }


        // =========================================================
        // 13. ENVIRONMENT AND VERSION VALIDATION
        // =========================================================

        stage('Validate Environment And Version') {

            steps {

                bat """
                    echo.
                    echo ===== APPLICATION RESPONSE =====

                    curl.exe --fail ^
                    http://localhost:${env.HOST_PORT}/
                """
            }
        }


        // =========================================================
        // 14. CUSTOMER SEARCH VALIDATION
        // =========================================================

        stage('Validate Customer Search') {

            steps {

                bat """
                    echo.
                    echo ===== CUSTOMER SEARCH =====

                    curl.exe --fail ^
                    http://localhost:${env.HOST_PORT}/customers/search
                """
            }
        }


        // =========================================================
        // 15. FINAL VALIDATION
        // =========================================================

        stage('Final Validation') {

            steps {

                bat """
                    echo.
                    echo ============================================================
                    echo FINAL DEPLOYMENT VALIDATION
                    echo ============================================================

                    echo Environment : ${env.ENV_NAME}
                    echo Branch      : ${env.TARGET_BRANCH}
                    echo Version     : ${params.VERSION}
                    echo Application : ${env.APP_CONTAINER}
                    echo Database    : ${env.DB_CONTAINER}
                    echo Network     : ${env.NETWORK_NAME}
                    echo Volume      : ${env.DB_VOLUME}
                    echo Port        : ${env.HOST_PORT}

                    echo.
                    echo ===== FINAL DOCKER STATUS =====
                    "${DOCKER}" ps

                    echo.
                    echo ===== FINAL NETWORK =====
                    "${DOCKER}" network inspect ${env.NETWORK_NAME}

                    echo.
                    echo ===== FINAL VOLUME =====
                    "${DOCKER}" volume inspect ${env.DB_VOLUME}

                    echo.
                    echo ============================================================
                    echo FINAL RESULT: SUCCESS
                    echo ============================================================
                """
            }
        }
    }


    // =============================================================
    // POST ACTIONS
    // =============================================================

    post {

        success {

            echo """
============================================================
JENKINS PIPELINE SUCCESS
============================================================

Environment : ${params.ENVIRONMENT}
Action      : ${params.ACTION}
Version     : ${params.VERSION}

Application : ${env.APP_CONTAINER}
Database    : ${env.DB_CONTAINER}
Network     : ${env.NETWORK_NAME}
Port        : ${env.HOST_PORT}

FINAL RESULT: SUCCESS
============================================================
"""
        }

        failure {

            echo """
============================================================
JENKINS PIPELINE FAILED
============================================================

Environment : ${params.ENVIRONMENT}
Action      : ${params.ACTION}
Version     : ${params.VERSION}

FINAL RESULT: FAILURE

Check the stage above for the exact failure.
============================================================
"""
        }

        always {

            echo "Jenkins pipeline execution completed."
        }
    }
}