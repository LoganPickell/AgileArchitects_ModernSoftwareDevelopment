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
    books = []
    query = None
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            try:
                response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={query}')
                if response.status_code == 200:
                    data = response.json()
                    books = data.get('items', [])
            except requests.RequestException:
                books = []

    return render_template('search_books.html', books=books, query=query)


if __name__ == '__main__':
    app.run(debug=True)
