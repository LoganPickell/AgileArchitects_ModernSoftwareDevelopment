from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

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

@app.route('/login', methods=['GET', 'POST'])
def login():
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

    return render_template('login.html', error=error)


@app.route('/dashboard')
def dashboard():
    username = request.args.get('username')
    return render_template('dashboard.html', username=username)

@app.route('/search_videos')
def search_videos():
    return render_template('search_videos.html') 

if __name__ == '__main__':
    app.run(debug=True)
