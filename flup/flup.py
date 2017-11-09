'''Main Flask application file.'''

import os

from flask import Flask, g, request

from .db import init_db

USAGE = '''flup is a simple pastebin: you upload a file and get a URL to
it (the file) as a response.
'''

def create_app(config=None):
    '''
    Application factory to create applications with multiple
    configuration options
    '''

    app = Flask(__name__)

    app.config.update(dict(
        DATABASE=os.path.join(app.root_path, 'flurl.db'),
    ))
    app.config.update(config or {})
    app.config.from_envvar('FLUP_SETTINGS', silent=True)

    register_cli(app)
    register_teardowns(app)
    register_routes(app)

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


def register_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            data = request.files.get('f')

            if not data:
                return ('no file provided\n', 400)

            try:
                app.logger.debug(data.read().decode()[:40] + '...')
            except:
                app.logger.debug('Couldn\'t decode file, probably a binary')
                return ('not ok\n', 400)

            return ('ok\n', 201)
        return USAGE
