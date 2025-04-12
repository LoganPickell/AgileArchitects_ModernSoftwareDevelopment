"""Testing the toggle_favorite endpoint in the app."""

# pylint: disable=bad-indentation
import pytest
from app import create_app, db
from app.models import BookShelf, Book, User

@pytest.fixture(name='test_client')
@pytest.mark.usefixtures('test_client')
def fixture_test_client():
    """Sets up pytest fixture for the test client."""
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
   user = User(username="testuser")
   db.session.add(user)
   db.session.commit()

   book = Book(title="Test Book", author="John Doe", genre="Fiction",
               image="/static/assets/img/DefaultBookCover.jpg")
   db.session.add(book)
   db.session.commit()

   shelf_entry = BookShelf(book_id=book.book_id, user_id=user.id,
                           hasRead=0, inCollection=0, isFavorite=0)
   db.session.add(shelf_entry)
   db.session.commit()

   with test_client.session_transaction() as session:
       session['user_id'] = user.id

    # Favoriting
   response = test_client.post(f'/toggle_favorite/{book.book_id}', follow_redirects=1)
   assert response.status_code == 200

   updated_entry = BookShelf.query.filter_by(user_id=user.id, book_id=book.book_id).first()
   assert updated_entry.isFavorite == 1

    # Unfavoriting
   response = test_client.post(f'/toggle_favorite/{book.book_id}', follow_redirects=1)
   assert response.status_code == 200

   updated_entry = BookShelf.query.filter_by(user_id=user.id, book_id=book.book_id).first()
   assert updated_entry.isFavorite == 0

def test_toggle_favorite_multiple(test_client):
    """Test favoriting multiple books."""
    user = User(username="testuser")
    db.session.add(user)
    db.session.commit()

    books = [Book(title=f"Test Book {i}", author="John Doe", genre="Fiction",
                  image="/static/assets/img/DefaultBookCover.jpg") for i in range(1, 10)]
    db.session.add_all(books)
    db.session.commit()

    shelf_entries = [BookShelf(book_id=book.book_id, user_id=user.id,
                               hasRead=0, inCollection=0, isFavorite=0) for book in books]
    db.session.add_all(shelf_entries)
    db.session.commit()


    with test_client.session_transaction() as session:
        session['user_id'] = user.id

    for book in books:
        response = test_client.post(f'/toggle_favorite/{book.book_id}', follow_redirects=1)
        assert response.status_code == 200
        updated_entry = BookShelf.query.filter_by(user_id=user.id, book_id=book.book_id).first()
        assert updated_entry.isFavorite == 1

def test_toggle_favorite_users(test_client):
   """Test different users favoriting and unfavoriting the same book."""
   users = [User(username=f"testuser{i}") for i in range(1, 4)]
   db.session.add_all(users)
   db.session.commit()

   book = Book(title="Test Book", author="John Doe", genre="Fiction",
               image="/static/assets/img/DefaultBookCover.jpg")
   db.session.add(book)
   db.session.commit()

   shelf_entries = [BookShelf(book_id=book.book_id, user_id=users[i].id,
                              hasRead=0, inCollection=0, isFavorite=0) for i in range(len(users))]
   db.session.add_all(shelf_entries)
   db.session.commit()

   with test_client.session_transaction() as session:
       session['user_id'] = users[0].id

   # Favoriting by User 1
   response = test_client.post(f'/toggle_favorite/{book.book_id}', follow_redirects=1)
   assert response.status_code == 200

   updated_entry = BookShelf.query.filter_by(user_id=users[0].id, book_id=book.book_id).first()
   assert updated_entry.isFavorite == 1

   # Favoriting by User 2
   with test_client.session_transaction() as session:
       session['user_id'] = users[1].id

   response = test_client.post(f'/toggle_favorite/{book.book_id}', follow_redirects=1)
   assert response.status_code == 200

   updated_entry = BookShelf.query.filter_by(user_id=users[1].id, book_id=book.book_id).first()
   assert updated_entry.isFavorite == 1

   # Favoriting by User 3
   with test_client.session_transaction() as session:
       session['user_id'] = users[2].id

   response = test_client.post(f'/toggle_favorite/{book.book_id}', follow_redirects=1)
   assert response.status_code == 200

   updated_entry = BookShelf.query.filter_by(user_id=users[2].id, book_id=book.book_id).first()
   assert updated_entry.isFavorite == 1

   # Unfavoriting (Only testing one user to ensure the others' favorites aren't affected)
   with test_client.session_transaction() as session:
       session['user_id'] = users[0].id

   response = test_client.post(f'/toggle_favorite/{book.book_id}', follow_redirects=1)
   assert response.status_code == 200

   updated_entry = BookShelf.query.filter_by(user_id=users[0].id, book_id=book.book_id).first()
   assert updated_entry.isFavorite == 0

   # Checks that User 2 and User 3 still have the book favorited
   updated_entry = BookShelf.query.filter_by(user_id=users[1].id, book_id=book.book_id).first()
   assert updated_entry.isFavorite == 1

   updated_entry = BookShelf.query.filter_by(user_id=users[2].id, book_id=book.book_id).first()
   assert updated_entry.isFavorite == 1
