import click
from flask import current_app, g
from flask.cli import with_appcontext
from flaskr import db

def get_db():
    if 'db' not in g:
        g.db = db
    return g.db

@click.command('create-db')
@with_appcontext
def createdb_command():
    """Clear the existing data and create new tables"""
    db.create_all()
    click.echo("Initialized the database")

def init_commands(app):
    app.cli.add_command(createdb_command)
