from . import db

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
    isFavorite = db.Column(db.Integer, default=0, nullable=False)
