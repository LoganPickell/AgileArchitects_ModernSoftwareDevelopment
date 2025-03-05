from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import requests
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    if request.method == 'POST':
        username = request.form['username']

        with sqlite3.connect("db.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, username FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()

            if user:
                session['user_id'] = user[0]
                session['username'] = user[1]
                return redirect(url_for('userBookShelf'))
            else:
                error = "Invalid username. Please try again."

    return render_template('home.html', error=error)

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    error = None
    if request.method == 'POST':
        username = request.form['username']

        with sqlite3.connect("db.sqlite") as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
                conn.commit()
                return redirect(url_for('home'))
            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint failed" in str(e):
                    error = "Username already exists. Try another one."

    return render_template('create_account.html', error=error)

@app.route('/userBookShelf')
def userBookShelf():
    user_id = session.get('user_id')
    username = session.get('username')

    if user_id is None:
        return redirect(url_for('home'))

    with sqlite3.connect("db.sqlite") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT b.title, b.author, b.genre, b.image, b.book_id, bs.hasRead, bs.inCollection FROM BOOK b JOIN BOOKSHELF bs ON b.book_id = bs.book_id WHERE bs.user_id = ?",
            (user_id,))
        books = cursor.fetchall()

    shelf_size = 8
    shelves = [books[i:i + shelf_size] for i in range(0, len(books), shelf_size)]

    return render_template('userBookShelf.html', username=username, shelves=shelves, shelf_size=shelf_size)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')
        image = request.form.get('cover_image') or '/static/assets/css/img/DefaultBookCover.jpg'
        user_id = session.get('user_id')
        username= session.get('username')

        hasRead = 1 if request.form.get('hasRead') else 0
        inCollection = 1 if request.form.get('inCollection') else 0

        with sqlite3.connect("db.sqlite") as conn:
            cursor = conn.cursor()

            cursor.execute("INSERT INTO BOOK (title, author, genre, image) VALUES (?, ?, ?, ?)",
                           (title, author, genre, image))
            conn.commit()

            book_id = cursor.lastrowid

            cursor.execute("INSERT INTO BOOKSHELF (book_id, user_id, hasRead, inCollection) VALUES (?, ?, ?, ?)",
                           (book_id, user_id, hasRead, inCollection))
            conn.commit()

        return redirect(url_for('userBookShelf'))

    return render_template('add_book.html')


@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if not book_id:
        return redirect(url_for('userBookshelf'))
    #prefill fields with info. from the database
    user_id = session.get('user_id') #Get the current user ID


    with sqlite3.connect("db.sqlite") as conn:
        cursor = conn.cursor()
       #Fetch book details along with has_read and in_collection
        #from BOOKSHELF
        cursor.execute("SELECT b.title, b.author, b.genre, b.image, bs.hasRead, bs.inCollection FROM BOOK b JOIN BOOKSHELF bs ON b.book_id=bs.book_id WHERE b.book_id = ? AND bs.user_id=?", (book_id,user_id))
        book = cursor.fetchone()

    if not book:
        return redirect(url_for('userBookshelf'))

    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')
        image = request.form.get('image')
        if not image: # If no new image is provided, keep the existing one
            image=book[3]

        hasRead = 1 if request.form.get('hasRead') else 0
        inCollection = 1 if request.form.get('inCollection') else 0

        with sqlite3.connect("db.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE BOOK SET title = ?, author = ?, genre = ?, image = ? WHERE book_id = ?",
                (title, author, genre, image, book_id)
            )
            cursor.execute(
                "UPDATE BOOKSHELF SET hasRead = ?, inCollection = ? WHERE book_id = ? AND user_id = ?",
                (hasRead, inCollection, book_id, user_id)
            )
            conn.commit()

        return redirect(url_for('userBookShelf'))
        # Convert tuple to dictionary for template rendering
        book= {
            "title": book[0],
            "author": book[1],
            "genre": book[2],
            "image": book[3],
            "hasRead": bool(book[4]),
            "inCollection": bool(book[5])
        }

    return render_template('edit_book.html', book=book)

@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if not book_id:
        return redirect(url_for('userBookShelf'))

    with sqlite3.connect("db.sqlite") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM BOOKSHELF WHERE book_id = ?", (book_id,))
        cursor.execute("DELETE FROM BOOK WHERE book_id = ?", (book_id,))
        conn.commit()

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
                    cover_image = volume_info.get('imageLinks', {}).get('thumbnail') or '/static/assets/css/img/DefaultBookCover.jpg'


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
    app.run(debug=True)
