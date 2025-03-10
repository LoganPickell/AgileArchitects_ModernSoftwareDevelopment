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


def test_home_get_rendering_elements(client):
    response = client.get("/")  #test the home route
    assert response.status_code == 200 #checks to see if client's request to server was successful
    assert b'<form method="POST">' in response.data #Ensures response contains expected HTML element, login form
    assert b'class="createAccBtn"' in response.data #ensure response contains create account btn

def test_home_create_account(client):
    response = client.get('/')
    assert b'class="createAccBtn"' in response.data  # Check if the button exists
    assert b'onclick="window.location.href=\'/create_account\'"' in response.data  # Check if redirect is correct

    response_redirect= client.get('/create_account', follow_redirects=True) #simulate clicking the button
    assert response_redirect.status_code==200 #verify the response redirects properly





