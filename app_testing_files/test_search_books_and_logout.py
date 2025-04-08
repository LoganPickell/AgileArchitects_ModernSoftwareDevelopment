import pytest
import os
from app import create_app, db
from app.models import BookShelf, Book, User


@pytest.fixture
def test_client():
    # Ensure correct path for templates and static folder
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'TEMPLATES_AUTO_RELOAD': True
    })

    with app.app_context():
        db.create_all()  # Ensure database tables are created
        yield app.test_client()  # Provide test client to the t


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





