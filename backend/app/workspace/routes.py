import json
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from backend.models.models import Project, Task, ProjectAnalysis, ActivityLog

workspace_bp = Blueprint('workspace', __name__, url_prefix='/workspace')

@workspace_bp.route('/dashboard')
@login_required
def dashboard():
    user_projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.updated_at.desc()).all()
    active_project = user_projects[0] if user_projects else None

    tasks = []
    analysis = None
    guidance = {}
    logs = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.timestamp.desc()).limit(10).all()

    if active_project:
        tasks = Task.query.filter_by(project_id=active_project.id).all()
        analysis = ProjectAnalysis.query.filter_by(project_id=active_project.id).first()
        if analysis and analysis.development_guidance_json:
            guidance = json.loads(analysis.development_guidance_json)

    return render_template(
        'workspace/dashboard.html',
        projects=user_projects,
        active_project=active_project,
        tasks=tasks,
        analysis=analysis,
        guidance=guidance,
        logs=logs
    )
