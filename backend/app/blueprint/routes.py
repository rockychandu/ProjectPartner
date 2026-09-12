import json
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.models.models import Project, ProjectBlueprint

blueprint_bp = Blueprint('blueprint', __name__, url_prefix='/blueprint')

@blueprint_bp.route('/view/<int:project_id>')
@login_required
def view_blueprint(project_id):
    project = Project.query.get_or_404(project_id)
    bp = ProjectBlueprint.query.filter_by(project_id=project.id).first_or_404()

    objectives = json.loads(bp.objectives or '[]')
    core_features = json.loads(bp.core_features or '[]')
    modules = json.loads(bp.modules_json or '[]')
    tech_stack = json.loads(bp.tech_stack_json or '[]')
    software_reqs = json.loads(bp.software_requirements or '[]')
    dev_phases = json.loads(bp.development_phases or '[]')

    return render_template(
        'blueprint/view.html',
        project=project,
        blueprint=bp,
        objectives=objectives,
        core_features=core_features,
        modules=modules,
        tech_stack=tech_stack,
        software_reqs=software_reqs,
        dev_phases=dev_phases
    )
