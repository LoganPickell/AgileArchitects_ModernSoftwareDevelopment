import sys
import os
import secrets
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

def test_add_book_default_image(test_client):
    with test_client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'test_user'

    test_client.post('/add_book', data={
        'title': 'Image Test Book',
        'author': 'Img Author',
        'genre': 'Horror',
        'cover_image': '',  # No image provided
        'hasRead': 'on',
        'inCollection': ''
    })

    book = Book.query.filter_by(title="Image Test Book").first()
    assert book is not None
    assert book.image == '/static/assets/img/DefaultBookCover.jpg'




#User Bookshelf
def test_user_bookshelf_normal(test_client):
    """Test displaying the user's bookshelf with books that can be deleted."""
    user = User(username=f"testuser")
    db.session.add(user)
    db.session.commit()

    book1 = Book(title="Book One", author="John Doe", genre="Fiction", image="/static/assets/img/DefaultBookCover.jpg")
    book2 = Book(title="Book Two", author="Jane Doe", genre="Non-Fiction",
                 image="/static/assets/img/DefaultBookCover.jpg")

    db.session.add_all([book1, book2])
    db.session.commit()

    shelf_entry1 = BookShelf(book_id=book1.book_id, user_id=user.id, hasRead=1, inCollection=1)
    shelf_entry2 = BookShelf(book_id=book2.book_id, user_id=user.id, hasRead=0, inCollection=1)

    db.session.add_all([shelf_entry1, shelf_entry2])
    db.session.commit()

    with test_client.session_transaction() as session:
        session['user_id'] = user.id

    db.session.delete(book1)
    db.session.commit()

    response = test_client.get('/userBookShelf')

    assert response.status_code == 200
    assert b"Book Two" in response.data
    assert b"Jane Doe" in response.data

def test_user_bookshelf_empty(test_client):
    """Test displaying the user's bookshelf without books."""
    user = User(username=f"testuser")
    db.session.add(user)
    db.session.commit()

    with test_client.session_transaction() as session:
        session['user_id'] = user.id

    response = test_client.get('/userBookShelf')

    assert response.status_code == 200