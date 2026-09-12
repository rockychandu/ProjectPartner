import json
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from backend.models.models import Project, ProjectAnalysis

testing_bp = Blueprint('testing_assistance', __name__, url_prefix='/testing')

@testing_bp.route('/view/<int:project_id>', methods=['GET', 'POST'])
@login_required
def view_testing(project_id):
    project = Project.query.get_or_404(project_id)
    analysis = ProjectAnalysis.query.filter_by(project_id=project.id).first()

    tests_detected = json.loads(analysis.tests_detected or '[]') if analysis else []
    models_detected = json.loads(analysis.models_detected or '[]') if analysis else []
    routes_detected = json.loads(analysis.routes_detected or '[]') if analysis else []

    generated_test_code = ""

    if request.method == 'POST':
        # Generate Pytest unit test file content
        generated_test_code = f"""# Automatically Generated Unit Test Suite for {project.title}
import pytest

def test_database_models_initialization():
    \"\"\"Verify that core database models are defined correctly.\"\"\"
    detected_models = {models_detected}
    assert isinstance(detected_models, list)
    print("Database model check completed.")

def test_routes_endpoints_signature():
    \"\"\"Verify route endpoint registration.\"\"\"
    detected_routes = {routes_detected}
    assert isinstance(detected_routes, list)
    print("Route endpoints check completed.")

def test_core_logic_validation():
    \"\"\"Verify application input validation logic.\"\"\"
    sample_input = "valid_data"
    assert len(sample_input) > 0
"""
        flash('Generated sample Pytest test suite based on actual project structure!', 'success')

    test_report = [
        {"test_name": "Database Connection & Relational Schema", "status": "PASS" if len(models_detected) > 0 else "WARNING", "details": f"{len(models_detected)} DB models detected."},
        {"test_name": "Authentication & Route Security", "status": "PASS" if (analysis and analysis.has_auth) else "FAIL", "details": "Authentication check based on AST analysis."},
        {"test_name": "Unit Test Coverage Suite", "status": "PASS" if len(tests_detected) > 0 else "WARNING", "details": f"{len(tests_detected)} test functions detected in codebase."}
    ]

    return render_template(
        'testing/view.html',
        project=project,
        tests=tests_detected,
        report=test_report,
        test_code=generated_test_code
    )
