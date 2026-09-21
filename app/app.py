from flask import Flask, jsonify
import os
import mysql.connector

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "5.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "DEV")

DB_HOST = os.getenv("DB_HOST", "customer-db-dev")
DB_USER = os.getenv("DB_USER", "customer_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "customer_password")
DB_NAME = os.getenv("DB_NAME", "customer_db")


def check_database():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        connection.close()
        return True
    except Exception:
        return False


def initialize_database():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL
            )
        """)

        cursor.execute("""
            INSERT INTO customers (name, email)
            SELECT 'Akanksha', 'akanksha@example.com'
            WHERE NOT EXISTS (
                SELECT 1 FROM customers
                WHERE email = 'akanksha@example.com'
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()

        print("Customer database initialized successfully")

    except Exception as error:
        print(f"Database initialization failed: {error}")


@app.route("/")
def home():
    return jsonify({
        "application": "Customer Platform",
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "database": "CONNECTED" if check_database() else "NOT CONNECTED"
    })


@app.route("/health")
def health():
    if check_database():
        return jsonify({
            "status": "UP",
            "version": APP_VERSION,
            "environment": ENVIRONMENT,
            "database": "CONNECTED"
        }), 200

    return jsonify({
        "status": "DOWN",
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "database": "NOT CONNECTED"
    }), 500


@app.route("/customers/search")
def customer_search():
    return jsonify({
        "feature": "customer-search",
        "status": "available"
    })


initialize_database()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)