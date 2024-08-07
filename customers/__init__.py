import os
from dotenv import load_dotenv
from flask import Flask
from customers import customers, database

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    app.json.sort_keys = False  # This prevents jsonify() to reorder keys within each row

    database.init_app(app)

    app.register_blueprint(customers.bp)

    print(f'Current environment: {os.getenv("ENVIRONMENT")}')
    print(f'Using database: {app.config.get("DATABASE")}')

    return app