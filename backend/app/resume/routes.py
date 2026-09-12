from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from backend.models.models import db, Project, ProjectBlueprint, ProjectAnalysis, ResumeEntry
from backend.algorithms.generators import DocPresentationResumeGenerator

resume_bp = Blueprint('resume', __name__, url_prefix='/resume')

@resume_bp.route('/view/<int:project_id>', methods=['GET', 'POST'])
@login_required
def view_resume(project_id):
    project = Project.query.get_or_404(project_id)
    blueprint = ProjectBlueprint.query.filter_by(project_id=project.id).first()
    analysis = ProjectAnalysis.query.filter_by(project_id=project.id).first()

    existing_entries = ResumeEntry.query.filter_by(project_id=project.id).all()

    if not existing_entries or request.method == 'POST':
        if existing_entries:
            for e in existing_entries:
                db.session.delete(e)

        generated = DocPresentationResumeGenerator.generate_resume_entries(project, blueprint, analysis)
        for item in generated:
            entry = ResumeEntry(
                project_id=project.id,
                category=item["category"],
                bullet_point=item["bullet_point"]
            )
            db.session.add(entry)
        db.session.commit()
        existing_entries = ResumeEntry.query.filter_by(project_id=project.id).all()
        flash('Generated fact-verified resume bullet points based on code analysis!', 'success')

    return render_template('resume/view.html', project=project, entries=existing_entries)
