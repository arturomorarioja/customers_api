import sqlite3
import click

from flask import current_app, g

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)

@click.command('init-db')
def init_db():
    db = get_db()

    with current_app.open_resource('customers.sql') as schema_and_data:
        db.executescript(schema_and_data.read().decode('utf-8'))

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def format_db_data(data):
    return {
        'customer_id': data[0],
        'first_name': data[1],
        'last_name': data[2],
        'phone_number': data[3],
        'address': data[4],
        'onboarding_date': data[5]
    }
