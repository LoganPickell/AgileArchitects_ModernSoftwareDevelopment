from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests

app = Flask(__name__)


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
                return redirect(url_for('dashboard', username=username))
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


@app.route('/dashboard')
def dashboard():
    username = request.args.get('username')
    return render_template('dashboard.html', username=username)

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
                    cover_image = volume_info.get('imageLinks', {}).get('thumbnail') or '/static/DefaultBookCover.jpg'
                      

                    book_details.append({
                        'title': title,
                        'authors': authors,
                        'genre': genre,
                        'cover_image': cover_image
                    })

            except requests.RequestException as e:
                print(f"Error fetching books: {e}")

    return render_template('search_books.html', books=book_details, query=query)


@app.route('/userBookShelf')
def userBookShelf():
    return render_template('userBookShelf.html')

if __name__ == '__main__':
    app.run(debug=True)
