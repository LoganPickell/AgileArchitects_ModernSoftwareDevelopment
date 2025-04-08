import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import secrets

db = SQLAlchemy()


def create_app(test_config=None):
    # Get the absolute paths of the 'templates' and 'static' directories
    base_dir = os.path.abspath(os.path.dirname(__file__))  # Path of the current file (run.py or app.py)

    app = Flask(__name__,
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static')
                )
    print(f"Template Folder: {app.template_folder}")
    print(f"Static Folder: {app.static_folder}")
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from .models import User, Book, BookShelf
    with app.app_context():
        db.create_all()

    from .routes import register_routes
    register_routes(app)

    return app
