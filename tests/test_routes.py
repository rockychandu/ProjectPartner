import pytest
from backend.app import create_app
from backend.models.models import db, User, Project, ProjectIdea

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            user = User.query.filter_by(email='unique_testroutes@college.edu').first()
            if not user:
                user = User(name='Route Test User', email='unique_testroutes@college.edu')
                user.set_password('pass123')
                db.session.add(user)
                db.session.flush()

            idea = ProjectIdea.query.filter_by(title='Test Proj Idea').first()
            if not idea:
                idea = ProjectIdea(
                    title='Test Proj Idea',
                    domain='Healthcare',
                    problem='Test problem',
                    solution='Test solution',
                    core_features='["F1"]',
                    technology_stack='["Python"]',
                    difficulty='Beginner',
                    estimated_duration_weeks=4,
                    team_size=2
                )
                db.session.add(idea)
                db.session.flush()

            proj = Project.query.filter_by(title='Test Proj Idea').first()
            if not proj:
                proj = Project(user_id=user.id, idea_id=idea.id, title='Test Proj Idea', domain='Healthcare')
                db.session.add(proj)
            db.session.commit()

            yield client

def test_new_routes_and_views(client):
    client.post('/auth/login', data={'email': 'unique_testroutes@college.edu', 'password': 'pass123'}, follow_redirects=True)

    # 1. Project Details
    det_resp = client.get('/projects/details/1')
    assert det_resp.status_code == 200

    # 2. Project Compare
    comp_resp = client.get('/projects/compare')
    assert comp_resp.status_code == 200

    # 3. Settings
    set_resp = client.get('/users/settings')
    assert set_resp.status_code == 200
