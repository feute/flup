"""Tests the Flup application."""

import os
import tempfile
import pytest

from flup.flup import create_app, USAGE
from flup.db import init_db, query_db
from io import BytesIO


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


def assert_text_plain_response(response):
    assert response.mimetype == 'text/plain'


def post_valid_file(client):
    """Submit valid data with POST to /"""
    rv = client.post('/', data={'f': (BytesIO(b'test'), 'test.txt')})
    return rv


def post_invalid_file(client):
    """Submit invalid data with POST to /"""
    rv = client.post('/', data={'f': (BytesIO(b'\x80'), 'test.txt')})
    return rv


def test_print_usage_on_root(client):
    """Print the usage string on GET /"""
    rv = client.get('/')
    assert_text_plain_response(rv)
    assert USAGE.encode() == rv.data


def test_success_on_post_valid_file(client):
    """Get 201 CREATED status code when submitting a valid
    POST request to /
    """
    rv = post_valid_file(client)
    assert rv.status_code == 201


def test_bad_request_on_post_invalid_file(client):
    """Get 400 BAD REQUEST status code when submitting an invalid
    POST request to /

    An invalid request in this case means a file that cannot be
    UTF-8 decoded.
    """
    rv = post_invalid_file(client)
    assert_text_plain_response(rv)
    assert rv.status_code == 400


def test_presence_of_valid_data_after_submit(client):
    """Assert the presence of valid data in the database after posting."""
    rv = post_valid_file(client)
    data = query_db('select * from bins')
    assert data


def test_absence_of_invalid_data_after_submit(client):
    """Assert the absence of invalid data in the database."""
    rv = post_invalid_file(client)
    data = query_db('select * from bins')
    assert not data


def test_get_by_identifier_returns_correct_data(client):
    """GET a previously uploaded file returns the correct data.

    The assertion should be made against the database data.
    """
    identifier = post_valid_file(client)
    identifier = identifier.data.decode().strip()
    data = query_db("select * from bins where name=?", [identifier],
                    one=True)
    rv = client.get('/' + identifier)

    assert data
    assert data['name'] == identifier
    assert data['content'] == rv.data.decode()
