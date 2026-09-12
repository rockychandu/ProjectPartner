import pytest
from backend.app import create_app
from backend.models.models import db, User

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

def test_user_registration_and_login(client):
    # Registration
    response = client.post('/auth/register', data={
        'name': 'Test Student',
        'email': 'student@test.com',
        'password': 'password123',
        'college': 'Test College',
        'branch': 'Computer Science',
        'year': '3rd Year'
    }, follow_redirects=True)
    assert response.status_code == 200

    with client.application.app_context():
        user = User.query.filter_by(email='student@test.com').first()
        assert user is not None
        assert user.name == 'Test Student'
        assert user.check_password('password123') is True
        assert user.profile is not None

    # Logout
    client.get('/auth/logout', follow_redirects=True)

    # Login
    response = client.post('/auth/login', data={
        'email': 'student@test.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
