import os
import sys
import pytest
from flask import Flask

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


#Testing for the logout endpoint
def test_logout(client):
    response = client.get("/logout")  # Test the logout route on the app
    assert response.status_code == 302  # Check if the response is a redirection.
    assert response.location == "/"  # Verify it redirects to the home page. Replace '/' if different.

def test_logout_wrong(client):
    response = client.get("/logot") #use incorrect route
    assert response.status_code == 404 #should return a not found


