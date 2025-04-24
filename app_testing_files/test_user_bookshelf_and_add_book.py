"""Testing the userBookshelf and add_book endpoints in the app."""

# pylint: disable=bad-indentation
import pytest
from app import create_app, db
from app.models import BookShelf, Book, User


@pytest.fixture
def test_client():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'TEMPLATES_AUTO_RELOAD': True,
    })

    with app.app_context():
        db.create_all()
        yield app.test_client()


# Add Book Tests
def test_add_book_get(test_client):
    """
        Test that the GET request to /add_book returns the form.

        Args:
            test_client: Flask test client.
        """
    response = test_client.get('/add_book')
    assert response.status_code == 200
    assert b'<form method="POST"' in response.data


def test_add_book_inserts_to_db(test_client):
    """
        Test that submitting the add book form inserts a book into the database.

        Args:
            test_client: Flask test client.
        """
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
    """
       Test that adding a book also creates a corresponding bookshelf entry.

       Args:
           test_client: Flask test client.
       """
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
    """
        Test that a default image is set when no cover image is provided.

        Args:
            test_client: Flask test client.
        """
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


# User Bookshelf
def test_user_bookshelf_normal(test_client):
    """Test displaying the user's bookshelf with books that can be deleted."""
    user = User(username="testuser")
    db.session.add(user)
    db.session.commit()

    book1 = Book(title="Book One", author="John Doe", genre="Fiction",
                 image="/static/assets/img/DefaultBookCover.jpg")
    book2 = Book(title="Book Two", author="Jane Doe", genre="Non-Fiction",
                 image="/static/assets/img/DefaultBookCover.jpg")

    db.session.add_all([book1, book2])
    db.session.commit()

    shelf_entry1 = BookShelf(book_id=book1.book_id, user_id=user.id,
                             hasRead=1, inCollection=1, isFavorite=0)
    shelf_entry2 = BookShelf(book_id=book2.book_id, user_id=user.id,
                             hasRead=0, inCollection=1, isFavorite=0)

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
    user = User(username="testuser")
    db.session.add(user)
    db.session.commit()

    with test_client.session_transaction() as session:
        session['user_id'] = user.id

    response = test_client.get('/userBookShelf')

    assert response.status_code == 200


def test_user_bookshelf_multiple(test_client):
    """Test displaying the user's bookshelf with multiple books."""
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

    response = test_client.get('/userBookShelf')

    assert response.status_code == 200
    assert b"Test Book 1" in response.data
    assert b"Test Book 2" in response.data
    assert b"Test Book 3" in response.data
    assert b"Test Book 4" in response.data
    assert b"Test Book 5" in response.data
    assert b"Test Book 6" in response.data
    assert b"Test Book 7" in response.data
    assert b"Test Book 8" in response.data
    assert b"Test Book 9" in response.data


def test_user_bookshelf_lengthy(test_client):
    """Test displaying the user's bookshelf with long words in all fields of a book."""
    user = User(username="testuser")
    db.session.add(user)
    db.session.commit()

    with test_client.session_transaction() as session:
        session["user_id"] = user.id

    long_word = 'L' * 300  # 300 characters long, no spaces
    test_client.post('/add_book', data={
        'title': long_word,
        'author': long_word,
        'genre': long_word,
        'description': long_word
     }, follow_redirects=True)

    response = test_client.get('/userBookShelf')

    # Makes sure the long word appears in the HTML
    html = response.get_data(as_text=True)
    assert long_word in html
