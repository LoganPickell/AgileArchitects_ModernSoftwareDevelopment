
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))
from flask import session

import pytest
from app import app, db, User, Book,BookShelf

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



#Add Book
def test_add_book_get(test_client):
    response = test_client.get('/add_book')
    assert response.status_code == 200
    assert b'<form method="POST"' in response.data

def test_add_book_redirection(test_client):
    response = test_client.get('/add_book')
    assert b'class="add_book_btn"' in response.data #check if btn exists
    assert b'onclick="window.location.href=\'/userBookshelf\'"' in response.data  # Check if redirect is correct
    response_redirect = test_client.get('/userBookshelf', follow_redirects=True)  # simulate clicking the button
    assert response_redirect.status_code == 200  # verify the response redirects properly

def test_add_book_inserts_to_db(test_client):
    #Test if submitting the add_book form actually inserts a book into the database
    # Simulate a user session
    with test_client.session_transaction() as sess:
        sess['user_id'] = 1  # Fake user ID
        sess['username'] = 'test_user'

    response = test_client.post('/add_book', data={
        'title': 'Database Test Book',
        'author': 'DB Author',
        'genre': 'Sci-Fi',
        'cover_image': '',
        'hasRead': 'on',
        'inCollection': 'on'
    }, follow_redirects=True)

    assert response.status_code == 200

    # Check if book was added
    book = Book.query.filter_by(title="Database Test Book").first()
    assert book is not None
    assert book.author == "DB Author"
    assert book.genre == "Sci-Fi"

def test_bookshelf_entry_created(test_client):
    """Test if adding a book creates an entry in BookShelf."""
    with test_client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'test_user'

    test_client.post('/add_book', data={
        'title': 'Bookshelf Test',
        'author': 'Shelf Author',
        'genre': 'Mystery',
        'cover_image': '',
        'hasRead': 'on',
        'inCollection': 'on'
    })

    book = Book.query.filter_by(title="Bookshelf Test").first()
    assert book is not None

    bookshelf_entry = BookShelf.query.filter_by(book_id=book.book_id, user_id=1).first()
    assert bookshelf_entry is not None
    assert bookshelf_entry.hasRead == 1
    assert bookshelf_entry.inCollection == 1
