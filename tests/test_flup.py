'''Tests the Flup application.'''

import os
import tempfile
import pytest

from flup.flup import create_app, USAGE
from flup.db import init_db


@pytest.fixture
def app(request):
    db_fd, temp_db_location = tempfile.mkstemp()
    config = {
        'DATABASE': temp_db_location,
        'TESTING': True,
        'DB_FD': db_fd,
    }

    app = create_app(config=config)

    with app.app_context():
        init_db()
        yield app


@pytest.fixture
def client(request, app):
    client = app.test_client()

    def teardown():
        os.close(app.config['DB_FD'])
        os.unlink(app.config['DATABASE'])

    request.addfinalizer(teardown)

    return client


def test_print_usage_on_root(client):
    '''
    Print the usage string on GET /
    '''

    rv = client.get('/')
    assert USAGE.encode() == rv.data
