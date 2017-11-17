"""Main Flask application file."""

import os

from flask import Flask, g, request

from .db import init_db

USAGE = """flup is a simple pastebin: you upload a file and get a URL to it
(the file) as a response.

the file must be uploaded with POST request to /, attaching the file to
a form field named 'f', and using the content-type multipart/form-data.

uploading a file with curl:
    $ curl -F 'f=@file.txt' localhost:5000

uploading a file with httpie:
    $ http -f localhost:5000 f@file.txt

uploading from stdin with curl:
    $ cat file.txt | curl -F 'f=@-' localhost:5000
"""


def create_app(config=None):
    """Create a Flask application with optional configuration options.

    config must be a dictionary containing the values that will be
    updated in the application.

    Return a Flask application with default configurations.
    """
    app = Flask(__name__)

    app.config.update(dict(
        DATABASE=os.path.join(app.root_path, 'flup.db'),
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
        """Initialise the database via command line.

        Usage:
            $ flask initdb
        """
        init_db()
        print('Initialised the database.')


def register_teardowns(app):
    @app.teardown_appcontext
    def close_db(error):
        """Close the database connection at the end of the request."""
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
                app.logger.debug("Couldn't decode file, probably a binary")
                return ('not ok\n', 400)

            return ('ok\n', 201)
        return USAGE
