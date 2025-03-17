import sys
import os
import pytest
import secrets
from app import app, db, Book, BookShelf, User


sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))


@pytest.fixture
def test_client():
   app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
   app.config['TESTING'] = True
   with app.app_context():
       db.create_all()
       yield app.test_client()
       db.drop_all()




def add_test_book(user_id):
   book = Book(title="Test Book", author="John Doe", genre="Fiction", image="/static/assets/img/DefaultBookCover.jpg")
   db.session.add(book)
   db.session.commit()


   book_shelf_entry = BookShelf(book_id=book.book_id, user_id=user_id, hasRead=0, inCollection=0)
   db.session.add(book_shelf_entry)
   db.session.commit()


   return book.book_id


def add_test_user():
   user = User(username=f"testuser_{secrets.token_hex(4)}") # Makes a different username for each user to avoid duplicates
   db.session.add(user)
   db.session.commit()
   return user


# Edit Book
def test_edit_book_normal(test_client):
   """Test editing a book's info correctly."""
   user = add_test_user()
   book_id = add_test_book(user.id)
   valid_data = {
       'title': 'Updated Title',
       'author': 'Updated Author',
       'genre': 'Updated Genre',
       'hasRead': '1',
       'inCollection': '1',
   }


   with test_client.session_transaction() as session:
       session['user_id'] = user.id
   response = test_client.post(f'/edit_book/{book_id}', data=valid_data)


   assert response.status_code == 302
   updated_book = Book.query.get(book_id)
   assert updated_book.title == valid_data['title']
   assert updated_book.author == valid_data['author']
   assert updated_book.genre == valid_data['genre']


   book_shelf_entry = BookShelf.query.filter_by(book_id=book_id).first()
   assert book_shelf_entry.hasRead == 1
   assert book_shelf_entry.inCollection == 1


def test_edit_book_empty(test_client):
   """Test editing a book's info with empty input."""
   user = add_test_user()
   book_id = add_test_book(user.id)


   invalid_data = {
       'title': '',
       'author': '',
       'genre': '',
       'hasRead': '1',
       'inCollection': '1',
   }


   with test_client.session_transaction() as session:
       session['user_id'] = user.id
   response = test_client.post(f'/edit_book/{book_id}', data=invalid_data)


   assert response.status_code == 400
   assert b"No spaces can be empty" in response.data


def test_edit_book_unauthorized(test_client):
   """Test editing a different user's book info."""
   user_1 = add_test_user()
   user_2 = add_test_user()
   book_id = add_test_book(user_1.id)


   unauthorized_data = {
       'title': 'Unauthorized Edit',
       'author': 'Updated Author',
       'genre': 'Updated Genre',
       'hasRead': '1',
       'inCollection': '1',
   }


   with test_client.session_transaction() as session:
       session['user_id'] = user_2.id
   response = test_client.post(f'/edit_book/{book_id}', data=unauthorized_data)


   assert response.status_code == 403
   unauthorized_book = Book.query.get(book_id)
   assert unauthorized_book.title != 'Unauthorized Edit'


def test_edit_book_nonexistent(test_client):
   """Test editing a nonexistent book."""
   user = add_test_user()
   nonexistent_book_id = 9999


   with test_client.session_transaction() as session:
       session['user_id'] = user.id


   response = test_client.post(f'/edit_book/{nonexistent_book_id}', data={'title': 'Nonexistent Book'})


   assert response.status_code == 404
   assert b'Book not found' in response.data


def test_edit_book_deleted(test_client):
   """Test editing a deleted book."""
   user = add_test_user()
   book_id = add_test_book(user.id)


   deleted_book = Book.query.get(book_id)
   db.session.delete(deleted_book)
   db.session.commit()


   with test_client.session_transaction() as session:
       session['user_id'] = user.id


   response = test_client.post(f'/edit_book/{book_id}', data={'title': 'Deleted Book'})


   assert response.status_code == 404
   assert b'Book not found' in response.data