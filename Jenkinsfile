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
                bat 'git fetch --all'

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
                    docker run --rm ^
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
                    docker build -t customer-app:${params.VERSION} .
                """

                bat """
                    docker image inspect customer-app:${params.VERSION}
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

                        /*
                         * VERSION 5.1 in PRODUCTION intentionally uses
                         * an invalid DB hostname.
                         *
                         * This demonstrates failed deployment
                         * followed by automatic rollback to 5.0.
                         */
                        def dbHost = env.DB_CONTAINER

                        if (
                            params.ENVIRONMENT == 'PRODUCTION' &&
                            params.ACTION == 'DEPLOY' &&
                            params.VERSION == '5.1'
                        ) {
                            dbHost = 'customer-db-prod-broken'
                            echo 'TEST SCENARIO: Using invalid DB hostname to demonstrate rollback.'
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
                                docker compose -p ${env.COMPOSE_PROJECT} up -d
                            """
                        }

                        echo 'Waiting for application to start...'

                        bat 'timeout /t 20 /nobreak >nul'

                        bat """
                            curl.exe --fail http://localhost:${env.HOST_PORT}/health
                        """

                        bat """
                            docker ps
                            docker network inspect ${env.NETWORK_NAME}
                        """

                        echo "FINAL RESULT: SUCCESS"

                    }

                    catch (Exception deploymentError) {

                        if (
                            params.ENVIRONMENT == 'PRODUCTION' &&
                            params.ACTION == 'DEPLOY' &&
                            params.VERSION == '5.1'
                        ) {

                            echo 'Deployment of version 5.1 failed.'
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
                                    docker compose -p ${env.COMPOSE_PROJECT} up -d
                                """
                            }

                            bat 'timeout /t 20 /nobreak >nul'

                            bat """
                                curl.exe --fail http://localhost:8083/health
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