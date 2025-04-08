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


# Testing for the logout endpoint
def test_logout(client):
    response = client.get("/logout")  # Test the logout route on the app
    assert response.status_code == 302  # Check if the response is a redirection.
    assert response.location == "/"  # Verify it redirects to the home page. Replace '/' if different.


def test_logout_wrong(client):
    response = client.get("/logot")  # use incorrect route
    assert response.status_code == 404  # should return a not found


#Test to ensure that the query is being stripped properly
def test_search_books_strip(client):
    #send the request from the client as a post, with the data included in the request
    response = client.post('/search_books', data={'query': ' harry '})
    #ensure that the response code is the 200 that is expected
    assert response.status_code == 200
    #make sure that the response includes the search term in some way
    assert 'harry' in response.data.decode()

#Testing that the result is returning all the html elements
def test_search_books_results(client):
    response = client.post('/search_books', data={'query': 'harry'})

    assert response.status_code == 200
    #now we need to check that our HTML elements are in the response
    assert '<div class="book-card2">' in response.data.decode()
    assert '<div class="book-info">' in response.data.decode()





