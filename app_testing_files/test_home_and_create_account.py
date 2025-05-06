import pytest
from app import create_app, db
from app.models import User


@pytest.fixture
def test_client():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'TEMPLATES_AUTO_RELOAD': True,
    })

    with app.app_context():
        db.create_all()
        yield app.test_client()


def test_home_get_rendering_elements(test_client):
    """
       Test GET / returns 200 and contains form and create account button.

       Args:
           test_client: Flask test client.
       """
    response = test_client.get("/")
    assert response.status_code == 200
    assert b'<form method="POST">' in response.data
    assert b'class="createAccBtn"' in response.data


def test_home_create_account_redirect(test_client):
    """
        Test that the create account button exists and redirects correctly.

        Args:
            test_client: Flask test client.
    """
    response = test_client.get('/')
    assert b'class="createAccBtn"' in response.data
    assert b'onclick="window.location.href=\'/create_account\'"' in response.data
    response_redirect = test_client.get('/create_account', follow_redirects=True)
    assert response_redirect.status_code == 200


def test_valid_login(test_client):
    """
        Test that a valid username logs in successfully and sets session variables.

        Args:
            test_client: Flask test client.
    """
    with test_client.application.app_context():
        user = User(username='testuser')
        db.session.add(user)
        db.session.commit()

    response = test_client.post('/', data={'username': 'testuser'}, follow_redirects=True)
    assert response.status_code == 200

    with test_client.session_transaction() as sess:
        assert sess.get('user_id') is not None
        assert sess.get('username') == 'testuser'


def test_invalid_login(test_client):
    """
        Test that login with an invalid username fails and shows error message.

        Args:
            test_client: Flask test client.
        """
    response = test_client.post('/', data={'username': 'nonexistent'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid username. Please try again." in response.data

    with test_client.session_transaction() as sess:
        assert sess.get('user_id') is None


def test_session_persistence(test_client):
    """
        Test that the session retains the username after login.

        Args:
            test_client: Flask test client.
        """
    with test_client.application.app_context():
        user = User(username='sessionuser')
        db.session.add(user)
        db.session.commit()

    test_client.post('/', data={'username': 'sessionuser'}, follow_redirects=True)
    with test_client.session_transaction() as sess:
        assert sess.get('username') == 'sessionuser'


def test_create_account_valid(test_client):
    response = test_client.post('/create_account', data={'username': 'newuser'})
    assert response.status_code == 302
    assert response.location == '/'

    with test_client.application.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.username == 'newuser'


def test_create_account_empty_username(test_client):
    response = test_client.post('/create_account', data={'username': ''})
    assert response.status_code == 400
    assert b"Username cannot be empty" in response.data


def test_create_account_case_sensitive(test_client):
    test_client.post('/create_account', data={'username': 'user'})
    response = test_client.post('/create_account', data={'username': 'User'})
    assert response.status_code == 400
    assert b"Username already exists" in response.data


def test_create_account_special_characters(test_client):
    response = test_client.post('/create_account', data={'username': 'user@123'})
    assert response.status_code == 400
    assert b"Invalid username: Only letters, numbers, and underscores are allowed" in response.data


def test_create_account_too_long_username(test_client):
    long_username = 'a' * 26
    response = test_client.post('/create_account', data={'username': long_username})
    assert response.status_code == 400
    assert b"Username is too long, keep it under 25 characters" in response.data


def test_create_account_sql_injection(test_client):
    sql_injection_username = "SELECT"
    response = test_client.post('/create_account', data={'username': sql_injection_username})
    assert response.status_code == 400
    assert b"Invalid username: possible SQL injection attempt" in response.data


def test_create_account_non_ascii(test_client):
    response = test_client.post('/create_account', data={'username': 'ユーザー'})
    assert response.status_code == 400
    assert b"Invalid username: Only letters, numbers, and underscores are allowed" in response.data


def test_create_account_duplicate_username(test_client):
    test_client.post('/create_account', data={'username': 'existinguser'})
    response = test_client.post('/create_account', data={'username': 'existinguser'})
    assert response.status_code == 400
    assert b"Username already exists" in response.data

def test_create_account_duplicate_username_case_sensitive(test_client):
    test_client.post('/create_account', data={'username': 'ExistingUser2'})
    response = test_client.post('/create_account', data={'username': 'existinguser2'})
    assert response.status_code == 400
    assert b"Username already exists" in response.data
