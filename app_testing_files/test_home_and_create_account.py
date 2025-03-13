import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))


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