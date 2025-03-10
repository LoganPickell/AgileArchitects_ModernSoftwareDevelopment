import os
import sys
import pytest
import requests
from unittest.mock import patch
from flask import Flask

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


#Add Book
def test_add_book(client):
    response = client.get('/add_book')
    assert response.status_code == 200
    assert b'<form method="POST"' in response.data

def test_add_book_redirection(client):
    response = client.get('/add_book')
    assert b'class="add_book_btn"' in response.data #check if btn exists

