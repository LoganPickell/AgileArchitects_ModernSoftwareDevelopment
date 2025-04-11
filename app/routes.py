import re
import requests
from flask import render_template, request, redirect, url_for, flash, session
from .models import User, Book, BookShelf
from . import db


def register_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    def home():
        if request.method == 'POST':
            username = request.form['username']

            user = User.query.filter_by(username=username).first()

            if user:
                session['user_id'] = user.id
                session['username'] = user.username
                return redirect(url_for('userBookShelf'))
            else:
                flash("Invalid username. Please try again.", "error")

        return render_template('home.html')

    def username_validation(username):
        if len(username) > 25:
            raise ValueError("Username is too long, keep it under 25 characters")

        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise ValueError("Invalid username: Only letters, numbers, and underscores are allowed")

        sql_injection_patterns = [
            r"(--|\#|\;)",
            r"(\b(SELECT|INSERT|DELETE|UPDATE|DROP|ALTER|CREATE|TRUNCATE|REPLACE)\b)",
            r"(\b(UNION|EXEC|EXECUTE|FETCH|DECLARE|CAST|CONVERT)\b)",
            r"(\b(OR|AND)\b.*?[=<>])",
            r"['\"\\]",
        ]

        for pattern in sql_injection_patterns:
            if re.search(pattern, username, re.IGNORECASE):
                raise ValueError("Invalid username: possible SQL injection attempt")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            raise ValueError("Username already exists")

        return username

    @app.route('/create_account', methods=['GET', 'POST'])
    def create_account():
        if request.method == 'POST':
            username = request.form['username'].lower()

            if not username:
                flash("Username cannot be empty", "error")
                return render_template('create_account.html',
                                       error="Username cannot be empty"), 400
            try:
                valid_new_user = username_validation(username)
                new_user = User(username=valid_new_user)
                db.session.add(new_user)
                db.session.commit()
                flash(f"Account created for {username}!", "success")
                return redirect(url_for('home')), 302

            except ValueError as e:
                flash(str(e), "error")
                return render_template('create_account.html', error=str(e)), 400

        return render_template('create_account.html')

    @app.route('/userBookShelf')
    def userBookShelf():
        user_id = session.get('user_id')
        username = session.get('username')

        if user_id is None:
            return redirect(url_for('home'))

        books = (db.session.query(
            Book.title, Book.author, Book.genre, Book.image, Book.book_id,
            BookShelf.hasRead, BookShelf.inCollection, BookShelf.isFavorite
            ).join(BookShelf, Book.book_id == BookShelf.book_id).filter
        (BookShelf.user_id == user_id).all())

        shelf_size = 8
        shelves = [books[i:i + shelf_size] for i in range(0, len(books), shelf_size)]
        return render_template('userBookShelf.html',
            username=username, shelves=shelves, shelf_size=shelf_size)

    @app.route('/add_book', methods=['GET', 'POST'])
    def add_book():
        if request.method == 'POST':
            title = request.form.get('title')
            author = request.form.get('author')
            genre = request.form.get('genre')
            image = request.form.get('cover_image') or '/static/assets/img/DefaultBookCover.jpg'
            user_id = session.get('user_id')
            hasRead = 1 if request.form.get('hasRead') else 0
            inCollection = 1 if request.form.get('inCollection') else 0

            book = Book(title=title, author=author, genre=genre, image=image)
            db.session.add(book)
            db.session.commit()

            book_shelf = BookShelf(book_id=book.book_id, user_id=user_id,
             hasRead=hasRead, inCollection=inCollection)
            db.session.add(book_shelf)
            db.session.commit()

            return redirect(url_for('userBookShelf'))

        return render_template('add_book.html')

    @app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
    def edit_book(book_id):
        if not book_id:
            return redirect(url_for('userBookShelf'))

        user_id = session.get('user_id')  # Get the current user ID

        if user_id is None:
            flash("You must be logged in to edit a book.", "error")
            return redirect(url_for('home')), 302

        # Fetch book details along with hasRead
        # and inCollection from BookShelf
        book = db.session.query(Book, BookShelf).join(BookShelf, Book.book_id
            == BookShelf.book_id).filter(Book.book_id == book_id,
            BookShelf.user_id == user_id).first()

        if not book:
            # Return 403 if the book does not belong to the user
            book_exists = Book.query.get(book_id)
            if book_exists:
                return "You do not have permission to edit this book", 403
            return "Book not found", 404  # Return 404 if the book does not exist

        book_data, book_shelf_data = book

        if request.method == 'POST':
            title = request.form.get('title')
            author = request.form.get('author')
            genre = request.form.get('genre')
            image = request.form.get('image') or book_data.image
            if not title or not author or not genre:
                return "No spaces can be empty", 400
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
                    response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q='
                                            f'{query}&maxResults=10', timeout=5)
                    response.raise_for_status()
                    data = response.json()
                    books = data.get('items', [])

                    for book in books:
                        volume_info = book.get('volumeInfo', {})
                        title = volume_info.get('title', 'No Title Available')
                        authors = ', '.join(volume_info.get('authors', ['Unknown Author']))
                        genre = ', '.join(volume_info.get('categories', ['Unknown Genre']))
                        cover_image = volume_info.get('imageLinks', {}).get(
                            'thumbnail') or '/static/assets/img/DefaultBookCover.jpg'

                        book_details.append({
                            'title': title,
                            'authors': authors,
                            'genre': genre,
                            'cover_image': cover_image
                        })

                except requests.RequestException as e:
                    print(f"Error fetching books: {e}")

        return render_template('search_books.html',
                               books=book_details, query=query)

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        session.pop('username', None)
        return redirect(url_for('home'))

    @app.route('/toggle_favorite/<int:book_id>', methods=['POST'])
    def toggle_favorite(book_id):
        user_id = session.get('user_id')

        if user_id is None:
            return redirect(url_for('home'))

        book_shelf_entry = (BookShelf.query.filter_by
                            (book_id=book_id, user_id=user_id).first())

        if book_shelf_entry:
            book_shelf_entry.isFavorite = not book_shelf_entry.isFavorite
            db.session.commit()

        return redirect(url_for('userBookShelf'))
