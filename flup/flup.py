"""Main Flask application file."""

import os

from flask import Flask, g, request

from .db import init_db, save_data, query_db

USAGE = """flup is a simple pastebin: you upload a file and get an identifier
as a response.

the identifier is later used to retrieve your data, with the format:
GET /<identifier>

the file must be uploaded with a POST request to /, attaching the file to
a form field named 'f', and using the content-type multipart/form-data.

when you upload a file, you get a the identifier to your data as a
response; you should save this to later retrieve your data.

uploading a file with curl:
    $ curl -F 'f=@file.txt' localhost:5000

uploading a file with httpie:
    $ http -f localhost:5000 f@file.txt

uploading from stdin with curl:
    $ cat file.txt | curl -F 'f=@-' localhost:5000

retrieving a file with curl:
    $ curl localhost:5000/<identifier>

retrieving a file with httpie:
    $ http :5000/<identifier>

say you get an identifier 'abc-123' as a response when you upload your
file:
    $ curl localhost:5000/abc-123
    $ http :5000/abc-123
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
    """Register commands to a Flask application."""
    @app.cli.command('initdb')
    def initdb_command():
        """Initialise the database via command line.

        Usage:
            $ flask initdb
        """
        init_db()
        print('Initialised the database.')


def register_teardowns(app):
    """Register tear-down functions to a Flask application."""
    @app.teardown_appcontext
    def close_db(error):
        """Close the database connection at the end of the request."""
        if hasattr(g, 'sqlite_db'):
            g.sqlite_db.close()


def register_routes(app):
    """Register routes to a Flask application."""
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            data = request.files.get('f')

            if not data:
                return ('no file provided\n', 400)

            identifier = save_data(data.read())
            if identifier is None:
                return ('could not upload the file\n', 400)

            return (identifier + '\n', 201)
        return USAGE

    @app.route('/<identifier>')
    def get_data(identifier):
        data = query_db("select content from bins where name=?",
                        [identifier], one=True)
        if not data:
            return ('could not retrieve your file, sorry\n', 404)

        return data[0]
