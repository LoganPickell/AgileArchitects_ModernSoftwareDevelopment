import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))
from flask import session

import pytest
from app import app, db, User

import logging
logging.basicConfig(level=logging.DEBUG)



@pytest.fixture
def test_client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    print(f"Before test: {app.config['SQLALCHEMY_DATABASE_URI']}")  # Debug
    with app.app_context():
        db.create_all()
        print(f"After test: {app.config['SQLALCHEMY_DATABASE_URI']}")  # Debug
        yield app.test_client()
        db.drop_all()


def test_home_get_rendering_elements(test_client):
    response = test_client.get("/")  # test the home route
    assert response.status_code == 200  # checks to see if client's request to server was successful
    assert b'<form method="POST">' in response.data  # Ensures response contains expected HTML element, login form
    assert b'class="createAccBtn"' in response.data  # ensure response contains create account btn


def test_home_create_account_redirect(test_client):
    response = test_client.get('/')
    assert b'class="createAccBtn"' in response.data  # Check if the button exists
    assert b'onclick="window.location.href=\'/create_account\'"' in response.data  # Check if redirect is correct
    response_redirect = test_client.get('/create_account', follow_redirects=True)  # simulate clicking the button
    assert response_redirect.status_code == 200  # verify the response redirects properly


def test_valid_login(test_client):
    #test logging in with a valid user
 with app.app_context():
    user=User(username='testuser')
    db.session.add(user)
    db.session.commit()
 with test_client:
    response=test_client.post('/', data={'username':'testuser'}, follow_redirects=True)
    assert response.status_code == 200
    assert session.get('user_id') is not None #User should be Logged in
    assert session.get('username')=='testuser'  #Username should be stored in session

def test_invalid_login(test_client):
    ##test logging in with an invalid user
    with test_client:
        response=test_client.post('/', data={'username':'nonexistent'}, follow_redirects=True)
        assert response.status_code == 200
        assert b"Invalid username. Please try again." in response.data  # Flash message should appear
        with app.app_context():
            assert session.get('user_id') is None  # No user should be logged in

def test_session_persistence(test_client):
    #Test if session is set after login.
 with app.app_context():
     user=User(username='sessionuser')
     db.session.add(user)
     db.session.commit()
 with test_client:
     test_client.post('/', data={'username': 'sessionuser'}, follow_redirects=True)
     assert session.get('username') == 'sessionuser'  # Ensure session stores username



def test_create_account_valid(test_client):
    print(f"During test: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"DB URI being used: {db.engine.url}")
    response = test_client.post('/create_account', data={'username': 'newuser'})
    assert response.status_code == 302
    assert response.location == '/'
    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert user.username == 'newuser'

def test_create_account_empty_username(test_client):
    response = test_client.post('/create_account', data={'username': ''})
    print(f"DB URI being used: {db.engine.url}")
    assert response.status_code == 400
    assert b"Username cannot be empty" in response.data

def test_create_account_case_sensitive(test_client):
    test_client.post('/create_account', data={'username': 'user'})
    response = test_client.post('/create_account', data={'username': 'User'})
    print(f"DB URI being used: {db.engine.url}")
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