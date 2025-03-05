from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import requests
import secrets

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=False)

class BookShelf(db.Model):
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    hasRead = db.Column(db.Integer, nullable=False)
    inCollection = db.Column(db.Integer, nullable=False)

@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    if request.method == 'POST':
        username = request.form['username']

        user = User.query.filter_by(username=username).first()

        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('userBookShelf'))
        else:
            error = "Invalid username. Please try again."

    return render_template('home.html', error=error)

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    error = None
    if request.method == 'POST':
        username = request.form['username']

        try:
            new_user = User(username=username)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            if "UNIQUE constraint failed" in str(e):
                error = "Username already exists. Try another one."

    return render_template('create_account.html', error=error)

@app.route('/userBookShelf')
def userBookShelf():
    user_id = session.get('user_id')
    username = session.get('username')

    if user_id is None:
        return redirect(url_for('home'))

    books = db.session.query(
        Book.title, Book.author, Book.genre, Book.image, Book.book_id,
        BookShelf.hasRead, BookShelf.inCollection
    ).join(BookShelf, Book.book_id == BookShelf.book_id).filter(BookShelf.user_id == user_id).all()

    shelf_size = 8
    shelves = [books[i:i + shelf_size] for i in range(0, len(books), shelf_size)]

    return render_template('userBookShelf.html', username=username, shelves=shelves, shelf_size=shelf_size)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')
        image = request.form.get('cover_image') or '/static/assets/img/DefaultBookCover.jpg'
        user_id = session.get('user_id')
        username = session.get('username')

        hasRead = 1 if request.form.get('hasRead') else 0
        inCollection = 1 if request.form.get('inCollection') else 0

        book = Book(title=title, author=author, genre=genre, image=image)
        db.session.add(book)
        db.session.commit()

        book_shelf = BookShelf(book_id=book.book_id, user_id=user_id, hasRead=hasRead, inCollection=inCollection)
        db.session.add(book_shelf)
        db.session.commit()

        return redirect(url_for('userBookShelf'))

    return render_template('add_book.html')

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if not book_id:
        return redirect(url_for('userBookShelf'))

    user_id = session.get('user_id')  # Get the current user ID

    # Fetch book details along with hasRead and inCollection from BookShelf
    book = db.session.query(Book, BookShelf).join(BookShelf, Book.book_id == BookShelf.book_id).filter(
        Book.book_id == book_id, BookShelf.user_id == user_id).first()

    if not book:
        return redirect(url_for('userBookShelf'))

    book_data, book_shelf_data = book

    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')
        image = request.form.get('image') or book_data.image  # Keep existing image if no new one is provided

        hasRead = 1 if request.form.get('hasRead') else 0
        inCollection = 1 if request.form.get('inCollection') else 0

        # Update book details
        book_data.title = title
        book_data.author = author
        book_data.genre = genre
        book_data.image = image

        # Update bookshelf details
        book_shelf_data.hasRead = hasRead
        book_shelf_data.inCollection = inCollection

        db.session.commit()

        return redirect(url_for('userBookShelf'))

    book_dict = {
        "title": book_data.title,
        "author": book_data.author,
        "genre": book_data.genre,
        "image": book_data.image,
        "hasRead": bool(book_shelf_data.hasRead),
        "inCollection": bool(book_shelf_data.inCollection),
    }

    return render_template(
        'edit_book.html',
        book=book_dict,
    )

@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if not book_id:
        return redirect(url_for('userBookShelf'))

    book_shelf_entry = BookShelf.query.filter_by(book_id=book_id).first()
    if book_shelf_entry:
        db.session.delete(book_shelf_entry)

    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)

    db.session.commit()

    return redirect(url_for('userBookShelf'))

@app.route('/search_books', methods=['GET', 'POST'])
def search_books():
    query = None
    book_details = []

    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            try:
                response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=10', timeout=5)
                response.raise_for_status()
                data = response.json()
                books = data.get('items', [])

                for book in books:
                    volume_info = book.get('volumeInfo', {})

                    title = volume_info.get('title', 'No Title Available')
                    authors = ', '.join(volume_info.get('authors', ['Unknown Author']))
                    genre = ', '.join(volume_info.get('categories', ['Unknown Genre']))
                    cover_image = volume_info.get('imageLinks', {}).get('thumbnail') or '/static/assets/img/DefaultBookCover.jpg'


                    book_details.append({
                        'title': title,
                        'authors': authors,
                        'genre': genre,
                        'cover_image': cover_image
                    })

            except requests.RequestException as e:
                print(f"Error fetching books: {e}")

    return render_template('search_books.html', books=book_details, query=query)



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
