'''Main Flask application file.'''

from flask import Flask


def create_app(config=None):
    '''
    Application factory to create applications with multiple
    configuration options
    '''

    app = Flask(__name__)
    app.config.update(config or {})
    app.config.from_envvar('FLUP_SETTINGS', silent=True)

    return app
