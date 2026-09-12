import pytest
import json
from backend.app import create_app
from backend.models.models import db, User, Project, Task, ProjectAnalysis

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

def test_full_student_end_to_end_workflow(client):
    # 1. Register Account
    reg_resp = client.post('/auth/register', data={
        'name': 'Alex Student',
        'email': 'alex@e2e.edu',
        'password': 'password123',
        'college': 'Tech Univ',
        'branch': 'Computer Science',
        'year': '3rd Year'
    }, follow_redirects=True)
    assert reg_resp.status_code == 200

    # Explicit Login to ensure session cookie persistence across test client redirects
    client.post('/auth/login', data={
        'email': 'alex@e2e.edu',
        'password': 'password123'
    }, follow_redirects=True)

    # 2. Update Student Profile
    prof_resp = client.post('/users/profile', data={
        'languages': ['Python', 'SQL'],
        'technologies': ['Flask', 'OpenCV'],
        'skills': ['Computer Vision', 'Backend'],
        'domains': ['Agriculture'],
        'available_time': 12,
        'preferred_difficulty': 'Intermediate',
        'team_preference': 'Team'
    }, follow_redirects=True)
    assert prof_resp.status_code == 200

    # 3. Generate Project Ideas
    gen_resp = client.post('/projects/generator', data={
        'domain': 'Agriculture',
        'technology': 'Python + Computer Vision',
        'difficulty': 'Intermediate',
        'duration': 8,
        'team_size': 3,
        'api_allowed': 'false',
        'hardware': 'Not Required'
    }, follow_redirects=True)
    assert gen_resp.status_code == 200

    # 4. Select Project (ID 1)
    sel_resp = client.post('/projects/select/1', follow_redirects=True)
    assert sel_resp.status_code == 200
    assert b"Blueprint" in sel_resp.data

    # 5. Manage Team & Allocate Roles
    team_resp = client.post('/teams/manage/1', data={
        'action': 'allocate_roles'
    }, follow_redirects=True)
    assert team_resp.status_code == 200

    # 6. View Task Distribution
    tasks_resp = client.get('/tasks/view/1')
    assert tasks_resp.status_code == 200
    assert b"Task Distribution" in tasks_resp.data or b"Task" in tasks_resp.data

    # 7. View Roadmap
    roadmap_resp = client.get('/roadmap/view/1')
    assert roadmap_resp.status_code == 200
    assert b"Development Timeline" in roadmap_resp.data or b"Roadmap" in roadmap_resp.data

    # 8. Run Project Analyzer
    analyzer_resp = client.post('/analyzer/view/1', data={}, follow_redirects=True)
    assert analyzer_resp.status_code == 200
    assert b"Blueprint vs. Actual" in analyzer_resp.data or b"Analyzer" in analyzer_resp.data

    # 9. Query Project Mentor
    mentor_resp = client.post('/mentor/chat/1', data=json.dumps({
        'query': 'What should I implement next?'
    }), content_type='application/json')
    assert mentor_resp.status_code == 200
    m_data = json.loads(mentor_resp.data)
    assert "response" in m_data

    # 10. Generate Documentation
    doc_resp = client.get('/documentation/view/1')
    assert doc_resp.status_code == 200
    assert b"SOFTWARE REQUIREMENTS SPECIFICATION" in doc_resp.data

    # 11. Download PDF Report Attachment
    pdf_resp = client.get('/documentation/download/1/pdf')
    assert pdf_resp.status_code == 200
    assert pdf_resp.mimetype == "application/pdf"
    assert len(pdf_resp.data) > 0

    # 12. Download SRS Document Attachment
    dl_resp = client.get('/documentation/download/1/srs')
    assert dl_resp.status_code == 200
    assert b"SOFTWARE REQUIREMENTS SPECIFICATION" in dl_resp.data
