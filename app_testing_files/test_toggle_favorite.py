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

def test_toggle_favorite_normal(test_client):
   """Test favoriting and unfavoriting a book's info correctly."""
   user = User(username=f"testuser")
   db.session.add(user)
   db.session.commit()

   book = Book(title="Test Book", author="John Doe", genre="Fiction", image="/static/assets/img/DefaultBookCover.jpg")
   db.session.add(book)
   db.session.commit()

   shelf_entry = BookShelf(book_id=book.book_id, user_id=user.id, hasRead=0, inCollection=0, isFavorite=0)
   db.session.add(shelf_entry)
   db.session.commit()

   with test_client.session_transaction() as session:
       session['user_id'] = user.id

    # Favoriting
   response = test_client.post(f'/toggle_favorite/{book.book_id}', follow_redirects=1)
   assert response.status_code == 200

   updated_entry = BookShelf.query.filter_by(user_id=user.id, book_id=book.book_id).first()
   assert updated_entry.isFavorite is 1

    # Unfavoriting
   response = test_client.post(f'/toggle_favorite/{book.book_id}', follow_redirects=1)
   assert response.status_code == 200

   updated_entry = BookShelf.query.filter_by(user_id=user.id, book_id=book.book_id).first()
   assert updated_entry.isFavorite is 0

def test_toggle_favorite_multiple(test_client):
    """Test favoriting multiple books."""
    user = User(username=f"testuser")
    db.session.add(user)
    db.session.commit()

    book_1 = Book(title="Test Book 1", author="John Doe", genre="Fiction",
                  image="/static/assets/img/DefaultBookCover.jpg")

    book_2 = Book(title="Test Book 2", author="John Doe", genre="Fiction",
                  image="/static/assets/img/DefaultBookCover.jpg")

    book_3 = Book(title="Test Book 3", author="John Doe", genre="Fiction",
                  image="/static/assets/img/DefaultBookCover.jpg")

    book_4 = Book(title="Test Book 4", author="John Doe", genre="Fiction",
                  image="/static/assets/img/DefaultBookCover.jpg")

    book_5 = Book(title="Test Book 5", author="John Doe", genre="Fiction",
                  image="/static/assets/img/DefaultBookCover.jpg")

    book_6 = Book(title="Test Book 6", author="John Doe", genre="Fiction",
                  image="/static/assets/img/DefaultBookCover.jpg")

    book_7 = Book(title="Test Book 7", author="John Doe", genre="Fiction",
                  image="/static/assets/img/DefaultBookCover.jpg")

    book_8 = Book(title="Test Book 8", author="John Doe", genre="Fiction",
                  image="/static/assets/img/DefaultBookCover.jpg")

    book_9 = Book(title="Test Book 9", author="John Doe", genre="Fiction",
                  image="/static/assets/img/DefaultBookCover.jpg")

    db.session.add_all([book_1, book_2, book_3, book_4, book_5, book_6, book_7, book_8, book_9])
    db.session.commit()

    shelf_entry1 = BookShelf(book_id=book_1.book_id, user_id=user.id, hasRead=0, inCollection=0, isFavorite=0)
    shelf_entry2 = BookShelf(book_id=book_2.book_id, user_id=user.id, hasRead=0, inCollection=0, isFavorite=0)
    shelf_entry3 = BookShelf(book_id=book_3.book_id, user_id=user.id, hasRead=0, inCollection=0, isFavorite=0)
    shelf_entry4 = BookShelf(book_id=book_4.book_id, user_id=user.id, hasRead=0, inCollection=0, isFavorite=0)
    shelf_entry5 = BookShelf(book_id=book_5.book_id, user_id=user.id, hasRead=0, inCollection=0, isFavorite=0)
    shelf_entry6 = BookShelf(book_id=book_6.book_id, user_id=user.id, hasRead=0, inCollection=0, isFavorite=0)
    shelf_entry7 = BookShelf(book_id=book_7.book_id, user_id=user.id, hasRead=0, inCollection=0, isFavorite=0)
    shelf_entry8 = BookShelf(book_id=book_8.book_id, user_id=user.id, hasRead=0, inCollection=0, isFavorite=0)
    shelf_entry9 = BookShelf(book_id=book_9.book_id, user_id=user.id, hasRead=0, inCollection=0, isFavorite=0)

    db.session.add_all([shelf_entry1, shelf_entry2, shelf_entry3, shelf_entry4, shelf_entry5,
                        shelf_entry6, shelf_entry7, shelf_entry8, shelf_entry9])
    db.session.commit()

    with test_client.session_transaction() as session:
        session['user_id'] = user.id

    response = test_client.post(f'/toggle_favorite/{book_1.book_id}', follow_redirects=1)
    assert response.status_code == 200

    updated_entry = BookShelf.query.filter_by(user_id=user.id, book_id=book_1.book_id).first()
    assert updated_entry.isFavorite is 1

    response = test_client.post(f'/toggle_favorite/{book_2.book_id}', follow_redirects=1)
    assert response.status_code == 200

    updated_entry = BookShelf.query.filter_by(user_id=user.id, book_id=book_2.book_id).first()
    assert updated_entry.isFavorite is 1

    response = test_client.post(f'/toggle_favorite/{book_3.book_id}', follow_redirects=1)
    assert response.status_code == 200

    updated_entry = BookShelf.query.filter_by(user_id=user.id, book_id=book_3.book_id).first()
    assert updated_entry.isFavorite is 1

    response = test_client.post(f'/toggle_favorite/{book_4.book_id}', follow_redirects=1)
    assert response.status_code == 200

    updated_entry = BookShelf.query.filter_by(user_id=user.id, book_id=book_4.book_id).first()
    assert updated_entry.isFavorite is 1

    response = test_client.post(f'/toggle_favorite/{book_5.book_id}', follow_redirects=1)
    assert response.status_code == 200

    updated_entry = BookShelf.query.filter_by(user_id=user.id, book_id=book_5.book_id).first()
    assert updated_entry.isFavorite is 1

    response = test_client.post(f'/toggle_favorite/{book_6.book_id}', follow_redirects=1)
    assert response.status_code == 200

    updated_entry = BookShelf.query.filter_by(user_id=user.id, book_id=book_6.book_id).first()
    assert updated_entry.isFavorite is 1

    response = test_client.post(f'/toggle_favorite/{book_7.book_id}', follow_redirects=1)
    assert response.status_code == 200

    updated_entry = BookShelf.query.filter_by(user_id=user.id, book_id=book_7.book_id).first()
    assert updated_entry.isFavorite is 1

    response = test_client.post(f'/toggle_favorite/{book_8.book_id}', follow_redirects=1)
    assert response.status_code == 200

    updated_entry = BookShelf.query.filter_by(user_id=user.id, book_id=book_8.book_id).first()
    assert updated_entry.isFavorite is 1

    response = test_client.post(f'/toggle_favorite/{book_9.book_id}', follow_redirects=1)
    assert response.status_code == 200

    updated_entry = BookShelf.query.filter_by(user_id=user.id, book_id=book_9.book_id).first()
    assert updated_entry.isFavorite is 1

def test_toggle_favorite_users(test_client):
   """Test different users favoriting and unfavoriting the same book."""
   user1 = User(username=f"testuser1")
   user2 = User(username=f"testuser2")
   user3 = User(username=f"testuser3")
   db.session.add_all([user1, user2, user3])
   db.session.commit()

   book = Book(title="Test Book", author="John Doe", genre="Fiction", image="/static/assets/img/DefaultBookCover.jpg")
   db.session.add(book)
   db.session.commit()

   shelf_entry1 = BookShelf(book_id=book.book_id, user_id=user1.id, hasRead=0, inCollection=0, isFavorite=0)
   shelf_entry2 = BookShelf(book_id=book.book_id, user_id=user2.id, hasRead=0, inCollection=0, isFavorite=0)
   shelf_entry3 = BookShelf(book_id=book.book_id, user_id=user3.id, hasRead=0, inCollection=0, isFavorite=0)
   db.session.add_all([shelf_entry1, shelf_entry2, shelf_entry3])
   db.session.commit()

   with test_client.session_transaction() as session:
       session['user_id'] = user1.id

   # Favoriting by User 1
   response = test_client.post(f'/toggle_favorite/{book.book_id}', follow_redirects=1)
   assert response.status_code == 200

   updated_entry = BookShelf.query.filter_by(user_id=user1.id, book_id=book.book_id).first()
   assert updated_entry.isFavorite is 1

   # Favoriting by User 2
   with test_client.session_transaction() as session:
       session['user_id'] = user2.id

   response = test_client.post(f'/toggle_favorite/{book.book_id}', follow_redirects=1)
   assert response.status_code == 200

   updated_entry = BookShelf.query.filter_by(user_id=user2.id, book_id=book.book_id).first()
   assert updated_entry.isFavorite is 1

   # Favoriting by User 3
   with test_client.session_transaction() as session:
       session['user_id'] = user3.id

   response = test_client.post(f'/toggle_favorite/{book.book_id}', follow_redirects=1)
   assert response.status_code == 200

   updated_entry = BookShelf.query.filter_by(user_id=user3.id, book_id=book.book_id).first()
   assert updated_entry.isFavorite is 1

   # Unfavoriting by User 1 (Only one user is being tested to ensure it doesn't affect others' favorites)
   with test_client.session_transaction() as session:
       session['user_id'] = user1.id

   response = test_client.post(f'/toggle_favorite/{book.book_id}', follow_redirects=1)
   assert response.status_code == 200

   updated_entry = BookShelf.query.filter_by(user_id=user1.id, book_id=book.book_id).first()
   assert updated_entry.isFavorite is 0

   # Checks that User 2 and User 3 still have the book favorited
   updated_entry = BookShelf.query.filter_by(user_id=user2.id, book_id=book.book_id).first()
   assert updated_entry.isFavorite is 1

   updated_entry = BookShelf.query.filter_by(user_id=user3.id, book_id=book.book_id).first()
   assert updated_entry.isFavorite is 1