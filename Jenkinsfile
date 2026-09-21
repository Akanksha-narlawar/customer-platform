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
            description: 'Required confirmation for production'
        )
    }

    stages {

        stage('Resolve Configuration') {
            steps {
                script {

                    def configs = [
                        DEV: [
                            branch: 'develop',
                            environment: 'DEV',
                            app: 'customer-app-dev',
                            db: 'customer-db-dev',
                            port: '8081',
                            network: 'customer-dev-net',
                            volume: 'customer-db-dev-data',
                            project: 'customer-dev'
                        ],

                        UAT: [
                            branch: 'release',
                            environment: 'UAT',
                            app: 'customer-app-uat',
                            db: 'customer-db-uat',
                            port: '8082',
                            network: 'customer-uat-net',
                            volume: 'customer-db-uat-data',
                            project: 'customer-uat'
                        ],

                        PRODUCTION: [
                            branch: 'main',
                            environment: 'PRODUCTION',
                            app: 'customer-app-prod',
                            db: 'customer-db-prod',
                            port: '8083',
                            network: 'customer-prod-net',
                            volume: 'customer-db-prod-data',
                            project: 'customer-prod'
                        ]
                    ]

                    if (!params.VERSION?.trim()) {
                        error('VERSION cannot be empty')
                    }

                    if (
                        params.ENVIRONMENT == 'PRODUCTION' &&
                        params.CONFIRM_PRODUCTION != 'YES'
                    ) {
                        error('Production deployment requires CONFIRM_PRODUCTION = YES')
                    }

                    if (
                        params.ENVIRONMENT != 'PRODUCTION' &&
                        params.CONFIRM_PRODUCTION == 'YES'
                    ) {
                        error('CONFIRM_PRODUCTION must be NO for DEV and UAT')
                    }

                    def config = configs[params.ENVIRONMENT]

                    if (config == null) {
                        error("Invalid environment: ${params.ENVIRONMENT}")
                    }

                    env.TARGET_BRANCH = config.branch
                    env.TARGET_ENVIRONMENT = config.environment
                    env.APP_CONTAINER = config.app
                    env.DB_CONTAINER = config.db
                    env.HOST_PORT = config.port
                    env.NETWORK_NAME = config.network
                    env.DB_VOLUME = config.volume
                    env.COMPOSE_PROJECT = config.project

                    echo """
================ RESOLVED CONFIGURATION ================

ENVIRONMENT : ${env.TARGET_ENVIRONMENT}
BRANCH      : ${env.TARGET_BRANCH}
ACTION      : ${params.ACTION}
VERSION     : ${params.VERSION}

APP         : ${env.APP_CONTAINER}
DATABASE    : ${env.DB_CONTAINER}
HOST PORT   : ${env.HOST_PORT}
NETWORK     : ${env.NETWORK_NAME}
DB VOLUME   : ${env.DB_VOLUME}
COMPOSE     : ${env.COMPOSE_PROJECT}

=========================================================
"""
                }
            }
        }

        stage('Checkout Selected Branch') {
            steps {

                bat '''
                    git fetch --all
                '''

                bat """
                    git checkout ${env.TARGET_BRANCH}
                    git reset --hard origin/${env.TARGET_BRANCH}
                """

                echo "Checked out branch: ${env.TARGET_BRANCH}"
            }
        }

        stage('Run Tests') {
            when {
                expression {
                    params.RUN_TESTS == 'YES'
                }
            }

            steps {

                bat '''
                    echo Checking Docker...

                    "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" version

                    echo Running tests...

                    "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" run --rm ^
                    -v "%WORKSPACE%:/workspace" ^
                    -w /workspace ^
                    python:3.12-slim ^
                    sh -c "pip install -q -r app/requirements.txt && pytest -q"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {

                bat """
                    echo Building Docker image...

                    "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" build -t customer-app:${params.VERSION} .
                """

                bat """
                    echo Checking Docker image...

                    "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" image inspect customer-app:${params.VERSION}
                """
            }
        }

        stage('Deploy / Rollback') {
            steps {

                script {

                    def dbPassword = ''

                    if (params.ENVIRONMENT == 'DEV') {
                        dbPassword = 'dev_password'
                    }
                    else if (params.ENVIRONMENT == 'UAT') {
                        dbPassword = 'uat_password'
                    }
                    else {
                        dbPassword = 'prod_password'
                    }

                    try {

                        def dbHost = env.DB_CONTAINER

                        /*
                         * Intentional failure scenario.
                         * Production version 5.1 uses an invalid DB hostname.
                         */
                        if (
                            params.ENVIRONMENT == 'PRODUCTION' &&
                            params.ACTION == 'DEPLOY' &&
                            params.VERSION == '5.1'
                        ) {

                            dbHost = 'customer-db-prod-broken'

                            echo '''
=========================================================
TEST SCENARIO
Version 5.1 uses an invalid DB hostname.
Deployment should fail.
Automatic rollback to version 5.0 will start.
=========================================================
'''
                        }

                        withEnv([
                            "IMAGE_NAME=customer-app:${params.VERSION}",
                            "APP_CONTAINER=${env.APP_CONTAINER}",
                            "DB_CONTAINER=${env.DB_CONTAINER}",
                            "DB_HOST=${dbHost}",
                            "HOST_PORT=${env.HOST_PORT}",
                            "NETWORK_NAME=${env.NETWORK_NAME}",
                            "DB_VOLUME=${env.DB_VOLUME}",
                            "APP_VERSION=${params.VERSION}",
                            "ENVIRONMENT=${env.TARGET_ENVIRONMENT}",
                            "DB_NAME=customer_db",
                            "DB_USER=customer_user",
                            "DB_PASSWORD=${dbPassword}",
                            "DB_ROOT_PASSWORD=${dbPassword}"
                        ]) {

                            bat """
                                echo Starting Docker Compose...

                                "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker-compose.exe" -p ${env.COMPOSE_PROJECT} up -d
                            """
                        }

                        echo 'Waiting for application to start...'

                        bat '''
                            timeout /t 20 /nobreak >nul
                        '''

                        echo 'Checking application health...'

                        bat """
                            curl.exe --fail http://localhost:${env.HOST_PORT}/health
                        """

                        echo 'Checking Docker containers...'

                        bat """
                            "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" ps
                        """

                        echo 'Checking Docker network...'

                        bat """
                            "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" network inspect ${env.NETWORK_NAME}
                        """

                        echo '========================================'
                        echo 'FINAL RESULT: SUCCESS'
                        echo '========================================'

                    }

                    catch (Exception deploymentError) {

                        if (
                            params.ENVIRONMENT == 'PRODUCTION' &&
                            params.ACTION == 'DEPLOY' &&
                            params.VERSION == '5.1'
                        ) {

                            echo 'Production version 5.1 deployment failed.'
                            echo 'Starting automatic rollback to version 5.0...'

                            withEnv([
                                "IMAGE_NAME=customer-app:5.0",
                                "APP_CONTAINER=${env.APP_CONTAINER}",
                                "DB_CONTAINER=${env.DB_CONTAINER}",
                                "DB_HOST=${env.DB_CONTAINER}",
                                "HOST_PORT=${env.HOST_PORT}",
                                "NETWORK_NAME=${env.NETWORK_NAME}",
                                "DB_VOLUME=${env.DB_VOLUME}",
                                "APP_VERSION=5.0",
                                "ENVIRONMENT=PRODUCTION",
                                "DB_NAME=customer_db",
                                "DB_USER=customer_user",
                                "DB_PASSWORD=prod_password",
                                "DB_ROOT_PASSWORD=prod_password"
                            ]) {

                                bat """
                                    echo Restoring version 5.0...

                                    "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker-compose.exe" -p ${env.COMPOSE_PROJECT} up -d
                                """
                            }

                            echo 'Waiting for rollback application...'

                            bat '''
                                timeout /t 20 /nobreak >nul
                            '''

                            echo 'Validating rollback...'

                            bat '''
                                curl.exe --fail http://localhost:8083/health
                            '''

                            bat """
                                "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" ps
                            """

                            echo '========================================'
                            echo 'FINAL RESULT: ROLLBACK'
                            echo 'Restored stable version: 5.0'
                            echo '========================================'

                            currentBuild.description = 'ROLLBACK: 5.1 -> 5.0'

                        }
                        else {
                            throw deploymentError
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution completed.'
        }
    }
}