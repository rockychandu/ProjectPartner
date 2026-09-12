import json
from backend.algorithms.generators import DocPresentationResumeGenerator

def test_fact_verified_documentation_generator():
    proj = type('obj', (object,), {'title': 'Agri Vision', 'domain': 'Agriculture', 'problem': 'Crop pests', 'status': 'Development'})
    blueprint = type('obj', (object,), {'tech_stack_json': 'Python, Flask'})
    analysis = type('obj', (object,), {
        'files_detected': '["app.py"]',
        'routes_detected': '["login"]',
        'models_detected': '[]',
        'tests_detected': '[]',
        'development_guidance_json': json.dumps({'has_auth': True, 'has_database': False, 'has_tests': False})
    })

    docs = DocPresentationResumeGenerator.generate_documentation(proj, blueprint, analysis)
    assert "Agri Vision" in docs['abstract']
    assert "Authentication module detected" in docs['srs_content']
    assert "Database models were not detected" in docs['srs_content'] # Non-fabrication check
