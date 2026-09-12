import json
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from backend.models.models import db, Project, ProjectBlueprint, ProjectAnalysis, Presentation
from backend.algorithms.generators import DocPresentationResumeGenerator

presentation_bp = Blueprint('presentation', __name__, url_prefix='/presentation')

@presentation_bp.route('/view/<int:project_id>', methods=['GET', 'POST'])
@login_required
def view_presentation(project_id):
    project = Project.query.get_or_404(project_id)
    blueprint = ProjectBlueprint.query.filter_by(project_id=project.id).first()
    analysis = ProjectAnalysis.query.filter_by(project_id=project.id).first()
    pres = Presentation.query.filter_by(project_id=project.id).first()

    if not pres or request.method == 'POST':
        slides_data = DocPresentationResumeGenerator.generate_presentation(project, blueprint, analysis)
        if not pres:
            pres = Presentation(project_id=project.id)
            db.session.add(pres)
        pres.slides_json = json.dumps(slides_data)
        db.session.commit()
        flash('Presentation slides generated!', 'success')

    slides = json.loads(pres.slides_json or '[]') if pres else []
    return render_template('presentation/view.html', project=project, slides=slides)
