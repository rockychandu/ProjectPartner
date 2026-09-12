import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from backend.models.models import db, Project, ProjectBlueprint, ProjectAnalysis, Documentation, ActivityLog
from backend.algorithms.generators import DocPresentationResumeGenerator

documentation_bp = Blueprint('documentation', __name__, url_prefix='/documentation')

@documentation_bp.route('/view/<int:project_id>', methods=['GET', 'POST'])
@login_required
def view_documentation(project_id):
    project = Project.query.get_or_404(project_id)
    blueprint = ProjectBlueprint.query.filter_by(project_id=project.id).first()
    analysis = ProjectAnalysis.query.filter_by(project_id=project.id).first()
    doc = Documentation.query.filter_by(project_id=project.id).first()

    if not doc or request.method == 'POST':
        generated_docs = DocPresentationResumeGenerator.generate_documentation(project, blueprint, analysis)
        
        if not doc:
            doc = Documentation(project_id=project.id)
            db.session.add(doc)

        doc.abstract = generated_docs['abstract']
        doc.srs_content = generated_docs['srs_content']
        doc.readme_content = generated_docs['readme_content']
        doc.full_report_content = generated_docs['full_report_content']

        # Log activity
        log = ActivityLog(user_id=current_user.id, action='Generated Documentation', details=f'Generated documentation for {project.title}')
        db.session.add(log)
        db.session.commit()

        flash('Documentation generated successfully from actual project state!', 'success')

    return render_template('documentation/view.html', project=project, doc=doc)


@documentation_bp.route('/download/<int:project_id>/<doc_type>')
@login_required
def download_documentation(project_id, doc_type):
    project = Project.query.get_or_404(project_id)
    doc = Documentation.query.filter_by(project_id=project.id).first()
    
    if not doc:
        flash('Please generate documentation first.', 'warning')
        return redirect(url_for('documentation.view_documentation', project_id=project.id))

    clean_title = "".join([c if c.isalnum() else "_" for c in project.title])

    if doc_type == 'pdf':
        blueprint = ProjectBlueprint.query.filter_by(project_id=project.id).first()
        pdf_bytes = DocPresentationResumeGenerator.generate_pdf_documentation(current_user, project, blueprint, doc)
        filename = f"{clean_title}_Documentation.pdf"
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    if doc_type == 'srs':
        content = doc.srs_content
        filename = f"{clean_title}_SRS.md"
        mimetype = "text/markdown"
    elif doc_type == 'readme':
        content = doc.readme_content
        filename = f"{clean_title}_README.md"
        mimetype = "text/markdown"
    else:
        content = doc.full_report_content
        filename = f"{clean_title}_Full_Report.txt"
        mimetype = "text/plain"

    return Response(
        content,
        mimetype=mimetype,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
