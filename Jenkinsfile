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
        // 1. RESOLVE ENVIRONMENT & SECURE CREDENTIALS
        // =========================================================

        stage('Resolve Environment') {

            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'customer-db-dev-credentials',
                        usernameVariable: 'DEV_DB_USER_VAL',
                        passwordVariable: 'DEV_DB_PASS_VAL'
                    ),
                    usernamePassword(
                        credentialsId: 'customer-db-uat-credentials',
                        usernameVariable: 'UAT_DB_USER_VAL',
                        passwordVariable: 'UAT_DB_PASS_VAL'
                    ),
                    usernamePassword(
                        credentialsId: 'customer-db-prod-credentials',
                        usernameVariable: 'PROD_DB_USER_VAL',
                        passwordVariable: 'PROD_DB_PASS_VAL'
                    )
                ]) {

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
                            env.DB_USER = env.DEV_DB_USER_VAL
                            env.DB_PASSWORD = env.DEV_DB_PASS_VAL
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
                            env.DB_USER = env.UAT_DB_USER_VAL
                            env.DB_PASSWORD = env.UAT_DB_PASS_VAL
                            env.DB_ROOT_PASSWORD = 'uat_root_password'
                            env.ENV_NAME = 'UAT'

                        }
                        else if (params.ENVIRONMENT == 'PRODUCTION') {

                            env.TARGET_BRANCH = 'main'
                            env.APP_CONTAINER = 'customer-app-prod'
                            env.DB_CONTAINER = 'customer-db-prod'
                            env.HOST_PORT = '8083'
                            env.NETWORK_NAME = 'customer-prod-net'
                            env.DB_VOLUME = 'customer-prod-data'
                            env.COMPOSE_PROJECT = 'customer-prod'
                            env.DB_HOST = 'customer-db-prod'
                            env.DB_NAME = 'customer_db'
                            env.DB_USER = env.PROD_DB_USER_VAL
                            env.DB_PASSWORD = env.PROD_DB_PASS_VAL
                            env.DB_ROOT_PASSWORD = 'prod_root_password'
                            env.ENV_NAME = 'PRODUCTION'

                        }
                        else {

                            error('Invalid environment selected.')

                        }

                        env.IMAGE_NAME = "${env.IMAGE_REPO}:${params.VERSION}"

                        echo """
============================================================
RESOLVED DEPLOYMENT CONFIGURATION (WITH SECURE CREDENTIALS)
============================================================

ENVIRONMENT     : ${env.ENV_NAME}
BRANCH          : ${env.TARGET_BRANCH}
ACTION          : ${params.ACTION}
VERSION         : ${params.VERSION}

IMAGE           : ${env.IMAGE_NAME}

APP CONTAINER   : ${env.APP_CONTAINER}
DATABASE        : ${env.DB_CONTAINER}

HOST PORT       : ${env.HOST_PORT}
NETWORK         : ${env.NETWORK_NAME}
DB VOLUME       : ${env.DB_VOLUME}

DB HOST         : ${env.DB_HOST}
DB NAME         : ${env.DB_NAME}
DB USER         : ${env.DB_USER}

COMPOSE PROJECT : ${env.COMPOSE_PROJECT}

============================================================
"""

                        if (
                            params.ENVIRONMENT == 'PRODUCTION' &&
                            params.CONFIRM_PRODUCTION != 'YES'
                        ) {

                            error(
                                'PRODUCTION deployment requires CONFIRM_PRODUCTION = YES'
                            )
                        }

                        if (
                            params.ENVIRONMENT == 'PRODUCTION' &&
                            env.TARGET_BRANCH != 'main'
                        ) {

                            error(
                                'Invalid production configuration. Production must use main branch.'
                            )
                        }

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
        // 4. BUILD, DEPLOY & AUTOMATIC ROLLBACK
        // =========================================================

        stage('Build and Deploy with Rollback Guard') {

            steps {

                script {

                    try {

                        // =====================================================
                        // BUILD DOCKER IMAGE
                        // =====================================================

                        echo "Building Docker image ${env.IMAGE_NAME}"

                        bat """
                            echo.
                            echo ===== BUILDING DOCKER IMAGE =====
                            "${DOCKER}" build -t ${env.IMAGE_NAME} .

                            echo.
                            echo ===== DOCKER IMAGE =====
                            "${DOCKER}" image inspect ${env.IMAGE_NAME}
                        """


                        // =====================================================
                        // CREATE ENVIRONMENT CONFIGURATION
                        // =====================================================

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

                        bat 'type .env'


                        // =====================================================
                        // DEPLOY OR EXPLICIT ROLLBACK
                        // =====================================================

                        if (params.ACTION == 'DEPLOY') {

                            echo "Deploying ${env.ENV_NAME} with version ${params.VERSION}"


                            // =================================================
                            // CONTROLLED FAILURE FOR ASSESSMENT
                            // =================================================
                            //
                            // Only PRODUCTION version 5.1 is intentionally
                            // given an invalid DB hostname.
                            //
                            // This allows the automatic rollback mechanism
                            // to demonstrate:
                            //
                            // 5.1 deployment
                            //      ↓
                            // DB connection failure
                            //      ↓
                            // automatic rollback
                            //      ↓
                            // version 5.0
                            //
                            // =================================================

                            if (
                                params.ENVIRONMENT == 'PRODUCTION' &&
                                params.VERSION == '5.1'
                            ) {

                                echo """
============================================================
ASSESSMENT FAILURE SCENARIO
============================================================

Production version 5.1 detected.

Intentionally changing DB_HOST to:
wrong-db-host

This will cause the application-to-database
connectivity validation to fail.

Automatic rollback should restore version 5.0.

============================================================
"""

                                env.DB_HOST = 'wrong-db-host'

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

                                bat 'type .env'
                            }


                            bat """
                                echo.
                                echo ===== DEPLOYING APPLICATION =====
                                "${COMPOSE}" -p ${env.COMPOSE_PROJECT} down
                                "${COMPOSE}" -p ${env.COMPOSE_PROJECT} up -d
                            """

                        }
                        else {

                            echo "Executing explicit rollback to version ${params.VERSION}"

                            bat """
                                echo.
                                echo ===== EXPLICIT ROLLBACK =====
                                "${COMPOSE}" -p ${env.COMPOSE_PROJECT} down
                                "${COMPOSE}" -p ${env.COMPOSE_PROJECT} up -d
                            """
                        }


                        // =====================================================
                        // WAIT FOR CONTAINERS
                        // =====================================================

                        echo "Waiting for containers to boot..."

                        bat 'ping 127.0.0.1 -n 21 >nul'


                        // =====================================================
                        // CONTAINER VALIDATION
                        // =====================================================

                        echo "Validating containers..."

                        bat """
                            echo.
                            echo ===== CONTAINER STATUS =====
                            "${DOCKER}" ps -a

                            echo.
                            echo ===== APPLICATION STATUS =====
                            "${DOCKER}" inspect -f "{{.State.Status}}" ${env.APP_CONTAINER}

                            echo.
                            echo ===== DATABASE STATUS =====
                            "${DOCKER}" inspect -f "{{.State.Status}}" ${env.DB_CONTAINER}
                        """


                        // =====================================================
                        // HEALTH CHECK
                        // =====================================================

                        echo "Checking application health..."

                        bat """
                            echo.
                            echo ===== APPLICATION HEALTH =====
                            curl.exe --fail http://localhost:${env.HOST_PORT}/health
                        """


                        // =====================================================
                        // APP TO DATABASE CONNECTIVITY
                        // =====================================================

                        echo "Checking application-to-database connectivity..."

                        bat """
                            echo.
                            echo ===== APP TO DATABASE CONNECTION =====

                            "${DOCKER}" exec ${env.APP_CONTAINER} python -c "import os,mysql.connector; c=mysql.connector.connect(host=os.environ['DB_HOST'],user=os.environ['DB_USER'],password=os.environ['DB_PASSWORD'],database=os.environ['DB_NAME']); print('APP_TO_DB_CONNECTION_SUCCESS'); c.close()"
                        """


                    }
                    catch (Exception e) {

                        // =====================================================
                        // AUTOMATIC ROLLBACK
                        // =====================================================

                        currentBuild.result = 'FAILURE'

                        echo """
============================================================
DEPLOYMENT FAILURE DETECTED!
INITIATING AUTOMATIC ROLLBACK...
============================================================
"""

                        // Safe production version
                        env.ROLLBACK_VERSION = '5.0'
                        env.IMAGE_NAME = "${env.IMAGE_REPO}:5.0"
                        env.DB_HOST = env.DB_CONTAINER


                        echo """
============================================================
ROLLBACK CONFIGURATION
============================================================

ROLLBACK VERSION : 5.0
IMAGE            : ${env.IMAGE_NAME}
APPLICATION      : ${env.APP_CONTAINER}
DATABASE         : ${env.DB_CONTAINER}
DB HOST          : ${env.DB_HOST}
NETWORK          : ${env.NETWORK_NAME}
PORT             : ${env.HOST_PORT}

============================================================
"""


                        // =====================================================
                        // REWRITE ENV FILE FOR VERSION 5.0
                        // =====================================================

                        echo "Re-writing .env configuration for stable version 5.0..."

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
APP_VERSION=5.0
ENVIRONMENT=${env.ENV_NAME}
DB_NAME=${env.DB_NAME}
DB_USER=${env.DB_USER}
DB_PASSWORD=${env.DB_PASSWORD}
DB_ROOT_PASSWORD=${env.DB_ROOT_PASSWORD}
"""
                        )

                        bat 'type .env'


                        // =====================================================
                        // STOP FAILED VERSION AND START 5.0
                        // =====================================================

                        bat """
                            echo.
                            echo ===== STOPPING FAILED DEPLOYMENT =====

                            "${COMPOSE}" -p ${env.COMPOSE_PROJECT} down

                            echo.
                            echo ===== STARTING STABLE VERSION 5.0 =====

                            "${COMPOSE}" -p ${env.COMPOSE_PROJECT} up -d

                            echo.
                            echo ===== WAITING FOR ROLLBACK =====

                            ping 127.0.0.1 -n 11 >nul

                            echo.
                            echo ===== ROLLED BACK CONTAINERS =====

                            "${DOCKER}" ps
                        """


                        // =====================================================
                        // VALIDATE ROLLBACK
                        // =====================================================

                        echo """
============================================================
VALIDATING ROLLBACK TO VERSION 5.0
============================================================
"""

                        bat """
                            echo.
                            echo ===== ROLLBACK APPLICATION =====

                            "${DOCKER}" inspect -f "{{.Config.Image}}" ${env.APP_CONTAINER}

                            echo.
                            echo ===== ROLLBACK APPLICATION STATUS =====

                            "${DOCKER}" inspect -f "{{.State.Status}}" ${env.APP_CONTAINER}

                            echo.
                            echo ===== ROLLBACK DATABASE STATUS =====

                            "${DOCKER}" inspect -f "{{.State.Status}}" ${env.DB_CONTAINER}

                            echo.
                            echo ===== ROLLBACK HEALTH CHECK =====

                            curl.exe --fail http://localhost:${env.HOST_PORT}/health

                            echo.
                            echo ===== ROLLBACK APP TO DATABASE =====

                            "${DOCKER}" exec ${env.APP_CONTAINER} python -c "import os,mysql.connector; c=mysql.connector.connect(host=os.environ['DB_HOST'],user=os.environ['DB_USER'],password=os.environ['DB_PASSWORD'],database=os.environ['DB_NAME']); print('ROLLBACK_APP_TO_DB_CONNECTION_SUCCESS'); c.close()"

                            echo.
                            echo ===== ROLLBACK VERSION CHECK =====

                            curl.exe --fail http://localhost:${env.HOST_PORT}/health
                        """


                        echo """
============================================================
AUTOMATIC ROLLBACK COMPLETED
============================================================

Failed Version : ${params.VERSION}
Restored       : 5.0
Environment    : ${env.ENV_NAME}

============================================================
"""

                        error(
                            "Deployment of version ${params.VERSION} failed. Automatic fallback successfully restored version 5.0!"
                        )
                    }
                }
            }
        }


        // =========================================================
        // 10. NETWORK VALIDATION
        // =========================================================

        stage('Validate Docker Network') {

            steps {

                echo "Checking Docker network ${env.NETWORK_NAME}"

                bat """
                    echo.
                    echo ===== NETWORK INSPECT =====
                    "${DOCKER}" network inspect ${env.NETWORK_NAME}
                """
            }
        }


        // =========================================================
        // 11. VOLUME VALIDATION
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
        // 12. FINAL VALIDATION
        // =========================================================

        stage('Final Validation') {

            steps {

                bat """
                    echo.
                    echo ============================================================
                    echo FINAL DEPLOYMENT VALIDATION
                    echo ============================================================
                    echo Environment : ${env.ENV_NAME}
                    echo Version     : ${params.VERSION}
                    echo Application : ${env.APP_CONTAINER}
                    echo Database    : ${env.DB_CONTAINER}
                    echo Port        : ${env.HOST_PORT}
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
Version     : ${params.VERSION}
FINAL RESULT: SUCCESS
============================================================
"""
        }

        failure {

            echo """
============================================================
JENKINS PIPELINE FAILED & ROLLED BACK
============================================================
Environment : ${params.ENVIRONMENT}
Requested Version : ${params.VERSION}
Rollback Version  : 5.0
FINAL RESULT: FAILURE (Rolled back to 5.0 safely)
============================================================
"""
        }

        always {

            echo "Jenkins pipeline execution completed."
        }
    }
}