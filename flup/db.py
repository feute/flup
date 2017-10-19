'''Database configuration file. SQLite is used for simplicity.'''

import sqlite3

from flask import g, current_app


def connect_db():
    '''
    Connects to the database specified in the config of the current
    application.
    '''

    rv = sqlite3.connect(current_app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    '''
    Opens a new connection to the database if there is none yet for
    the current application context.
    '''

    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()

    return g.sqlite_db


def init_db():
    '''
    Initialises the database by reading the schema file.
    '''

    db = get_db()

    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

    db.commit()


def query_db(query, args=(), one=False):
    '''
    Queries the database of the current app with the optional argument
    `args`, which will be passed to the query itself. Returns one result
    if the argument `one` is true.
    '''

    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()

    return (rv[0] if rv else None) if one else rv
