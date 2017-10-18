'''Main Flask application file.'''

from flask import Flask, g

from .db import init_db


def create_app(config=None):
    '''
    Application factory to create applications with multiple
    configuration options
    '''

    app = Flask(__name__)
    app.config.update(config or {})
    app.config.from_envvar('FLUP_SETTINGS', silent=True)

    register_cli(app)
    register_teardowns(app)

    return app


def register_cli(app):
    @app.cli.command('initdb')
    def initdb_command():
        '''
        Initialise the database via command line, usage:
            $ flask initdb
        '''

        init_db()
        print('Initialised the database.')


def register_teardowns(app):
    @app.teardown_appcontext
    def close_db(error):
        '''
        Closes the database connection at the end of the request.
        '''

        if hasattr(g, 'sqlite_db'):
            g.sqlite_db.close()
