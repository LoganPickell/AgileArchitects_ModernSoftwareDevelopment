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

# Edit Book
def test_edit_book_normal(test_client):
   """Test editing a book's info correctly."""
   user = User(username=f"testuser")
   db.session.add(user)
   db.session.commit()

   book = Book(title="Test Book", author="John Doe", genre="Fiction", image="/static/assets/img/DefaultBookCover.jpg")
   db.session.add(book)
   db.session.commit()

   book_shelf_entry = BookShelf(book_id=book.book_id, user_id=user.id, hasRead=0, inCollection=0)
   db.session.add(book_shelf_entry)
   db.session.commit()

   valid_data = {
       'title': 'Updated Title',
       'author': 'Updated Author',
       'genre': 'Updated Genre',
       'hasRead': '1',
       'inCollection': '1',
   }

   with test_client.session_transaction() as session:
       session['user_id'] = user.id
   response = test_client.post(f'/edit_book/{book.book_id}', data=valid_data)

   assert response.status_code == 302
   updated_book = Book.query.get(book.book_id)
   assert updated_book.title == valid_data['title']
   assert updated_book.author == valid_data['author']
   assert updated_book.genre == valid_data['genre']

   book_shelf_entry = BookShelf.query.filter_by(book_id=book.book_id).first()
   assert book_shelf_entry.hasRead == 1
   assert book_shelf_entry.inCollection == 1

def test_edit_book_empty(test_client):
   """Test editing a book's info with empty input."""
   user = User(username=f"testuser")
   db.session.add(user)
   db.session.commit()

   book = Book(title="Test Book", author="John Doe", genre="Fiction", image="/static/assets/img/DefaultBookCover.jpg")
   db.session.add(book)
   db.session.commit()

   book_shelf_entry = BookShelf(book_id=book.book_id, user_id=user.id, hasRead=0, inCollection=0)
   db.session.add(book_shelf_entry)
   db.session.commit()

   invalid_data = {
       'title': '',
       'author': '',
       'genre': '',
       'hasRead': '1',
       'inCollection': '1',
   }

   with test_client.session_transaction() as session:
       session['user_id'] = user.id
   response = test_client.post(f'/edit_book/{book.book_id}', data=invalid_data)

   assert response.status_code == 400
   assert b"No spaces can be empty" in response.data

def test_edit_book_unauthorized(test_client):
   """Test editing a different user's book info."""
   user_1 = User(username=f"testuser_1")
   user_2 = User(username=f"testuser_2")
   db.session.add_all([user_1, user_2])
   db.session.commit()

   book = Book(title="Test Book", author="John Doe", genre="Fiction", image="/static/assets/img/DefaultBookCover.jpg")
   db.session.add(book)
   db.session.commit()

   book_shelf_entry = BookShelf(book_id=book.book_id, user_id=user_1.id, hasRead=0, inCollection=0)
   db.session.add(book_shelf_entry)
   db.session.commit()

   unauthorized_data = {
       'title': 'Unauthorized Edit',
       'author': 'Updated Author',
       'genre': 'Updated Genre',
       'hasRead': '1',
       'inCollection': '1',
   }

   with test_client.session_transaction() as session:
       session['user_id'] = user_2.id
   response = test_client.post(f'/edit_book/{book.book_id}', data=unauthorized_data)

   assert response.status_code == 403
   unauthorized_book = Book.query.get(book.book_id)
   assert unauthorized_book.title != 'Unauthorized Edit'

def test_edit_book_nonexistent(test_client):
   """Test editing a nonexistent book."""
   user = User(username=f"testuser")
   db.session.add(user)
   db.session.commit()

   nonexistent_book_id = 9999

   with test_client.session_transaction() as session:
       session['user_id'] = user.id

   response = test_client.post(f'/edit_book/{nonexistent_book_id}', data={'title': 'Nonexistent Book'})

   assert response.status_code == 404
   assert b'Book not found' in response.data

def test_edit_book_deleted(test_client):
   """Test editing a deleted book."""
   user = User(username=f"testuser")
   db.session.add(user)
   db.session.commit()

   book = Book(title="Test Book", author="John Doe", genre="Fiction", image="/static/assets/img/DefaultBookCover.jpg")
   db.session.add(book)
   db.session.commit()

   book_id = book.book_id

   book_shelf_entry = BookShelf(book_id=book.book_id, user_id=user.id, hasRead=0, inCollection=0)
   db.session.add(book_shelf_entry)
   db.session.commit()

   db.session.delete(book)
   db.session.commit()

   with test_client.session_transaction() as session:
       session['user_id'] = user.id

   response = test_client.post(f'/edit_book/{book_id}', data={'title': 'Deleted Book'})

   assert response.status_code == 404
   assert b'Book not found' in response.data