"""Testing the edit_book and delete_book endpoints in the app."""

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


# Edit Book
def test_edit_book_normal(test_client):
    """Test editing a book's info correctly."""
    user = User(username="testuser")
    db.session.add(user)
    db.session.commit()

    book = Book(title="Test Book", author="John Doe", genre="Fiction",
                image="/static/assets/img/DefaultBookCover.jpg")
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
    updated_book = db.session.get(Book, book.book_id)
    assert updated_book.title == valid_data['title']
    assert updated_book.author == valid_data['author']
    assert updated_book.genre == valid_data['genre']

    book_shelf_entry = db.session.execute(
        db.select(BookShelf).filter_by(book_id=book.book_id)
    ).scalar_one_or_none()
    assert book_shelf_entry.hasRead == 1
    assert book_shelf_entry.inCollection == 1


def test_edit_book_empty(test_client):
    """Test editing a book's info with empty input."""
    user = User(username="testuser")
    db.session.add(user)
    db.session.commit()

    book = Book(title="Test Book", author="John Doe", genre="Fiction",
                image="/static/assets/img/DefaultBookCover.jpg")
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
    users = [User(username=f"testuser{i}") for i in range(1, 3)]
    db.session.add_all(users)
    db.session.commit()

    book = Book(title="Test Book", author="John Doe", genre="Fiction",
                image="/static/assets/img/DefaultBookCover.jpg")
    db.session.add(book)
    db.session.commit()

    book_shelf_entry = BookShelf(book_id=book.book_id, user_id=users[0].id,
                                 hasRead=0, inCollection=0)
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
        session['user_id'] = users[1].id
    response = test_client.post(f'/edit_book/{book.book_id}', data=unauthorized_data)

    assert response.status_code == 403
    unauthorized_book = db.session.get(Book, book.book_id)
    assert unauthorized_book.title != 'Unauthorized Edit'


def test_edit_book_nonexistent(test_client):
    """Test editing a nonexistent book."""
    user = User(username="testuser")
    db.session.add(user)
    db.session.commit()

    nonexistent_book_id = 9999

    with test_client.session_transaction() as session:
        session['user_id'] = user.id

    response = test_client.post(f'/edit_book/{nonexistent_book_id}',
                                data={'title': 'Nonexistent Book'})

    assert response.status_code == 404
    assert b'Book not found' in response.data


def test_edit_book_deleted(test_client):
    """Test editing a deleted book."""
    user = User(username="testuser")
    db.session.add(user)
    db.session.commit()

    book = Book(title="Test Book", author="John Doe", genre="Fiction",
                image="/static/assets/img/DefaultBookCover.jpg")
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


#  -------
# Delete book tests
def create_book(book_id=22, title='Test', author='Author', genre='Genre', image='img.jpg'):
    book22 = Book(book_id=book_id, title=title, author=author, genre=genre, image=image)
    db.session.add(book22)
    db.session.commit()
    return book22


def create_bookshelf_entry(user_id, book_id, hasRead=False, inCollection=True, isFavorite=False):
    entry = BookShelf(user_id=user_id, book_id=book_id, hasRead=hasRead, inCollection=inCollection,
                      isFavorite=isFavorite)
    db.session.add(entry)
    db.session.commit()
    return entry


def test_delete_book_success(client):
    with client.application.app_context():
        with client.session_transaction() as sess:
            sess['user_id'] = 22
            sess['username'] = 'tester'

        book = create_book(22)
        create_bookshelf_entry(user_id=22, book_id=book.book_id)

        response = client.post('/delete_book/22', follow_redirects=True)

        assert response.status_code == 200
        assert db.session.get(Book, 22) is None

        bookshelf = db.session.execute(
            db.select(BookShelf).filter_by(book_id=22)
        ).scalar_one_or_none()

        assert bookshelf is None


def test_delete_book_not_exists(client):
    with client.application.app_context():
        with client.session_transaction() as sess:
            sess['user_id'] = 22
            sess['username'] = 'tester'

        response = client.post('/delete_book/999', follow_redirects=True)

        assert response.status_code == 200  # Still redirects
        assert db.session.get(Book, 999) is None


def test_delete_book_no_bookshelf_entry(client):
    with client.application.app_context():
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'tester'

        create_book(55)

        response = client.post('/delete_book/55', follow_redirects=True)

        assert response.status_code == 200
        assert db.session.get(Book, 55) is None


def test_delete_book_no_book_but_bookshelf_entry_exists(client):
    with client.application.app_context():
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'tester'

        create_bookshelf_entry(user_id=23, book_id=33)

        response = client.post('/delete_book/33', follow_redirects=True)

        assert response.status_code == 200

        bookshelf = db.session.execute(
            db.select(BookShelf).filter_by(book_id=33)
        ).scalar_one_or_none()

        assert bookshelf is None
