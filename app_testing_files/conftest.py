import pytest
from app import create_app, db
import os


@pytest.fixture
def client():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'template_folder': os.path.join(os.path.dirname(__file__), 'app', 'templates'),
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
