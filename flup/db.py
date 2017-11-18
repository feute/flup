"""Database configuration file."""

import sqlite3
from secrets import token_urlsafe

from flask import g, current_app


def connect_db():
    """Connect to the database of the current application.

    The database connection string (in this case, the filename of the
    database) is taken from the value of the DATABASE key defined in
    the configuration of the current application.

    Return the database connection object.
    """
    rv = sqlite3.connect(current_app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Open a new connection to the database.

    If there is no connection open (which is determine by retrieving
    the connection from a global object), then open a new connection
    and save it for further use.

    Return the database connection object.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()

    return g.sqlite_db


def init_db(filename='schema.sql'):
    """Initialise the database by reading the schema file."""
    db = get_db()

    with current_app.open_resource(filename, mode='r') as f:
        db.cursor().executescript(f.read())

    db.commit()


def query_db(query, args=(), one=False):
    """Query the database of the current application.

    Return the first row of the result if the optional argument 'one'
    is true, or the whole query result if not specified.
    """
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()

    return (rv[0] if rv else None) if one else rv


def save_data(content):
    """Save text data to the database.

    The data is UTF-8 decoded before it is saved to the database.

    A random URL-safe name is generated to identify the data.  This
    identifier is meant to be used by users to retrieve the data that
    they uploaded.

    Return the identifier for the data.
    """
    try:
        content = content.decode()
    except UnicodeDecodeError:
        return None

    # Use a URL length of 4 bytes.
    name = token_urlsafe(4)
    db = get_db()

    db.execute('insert into bins (name, content) values (?, ?)',
               [name, content])
    db.commit()

    return name
