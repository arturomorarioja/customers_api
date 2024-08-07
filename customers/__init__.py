"""
Customers sample API

Author: Arturo Mora-Rioja
Date: August 2024
"""
import os
from dotenv import load_dotenv
from flask import Flask
from customers import customers, database

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    # This prevents jsonify() to reorder keys within each row
    app.json.sort_keys = False  

    database.init_app(app)

    app.register_blueprint(customers.bp)

    print(f'Current environment: {os.getenv("ENVIRONMENT")}')
    print(f'Using database: {app.config.get("DATABASE")}')

    return app