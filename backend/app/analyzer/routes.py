import os
import json
import zipfile
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from backend.models.models import db, Project, ProjectBlueprint, ProjectAnalysis, ActivityLog
from backend.algorithms.ast_analyzer import ProjectDirectoryAnalyzer, BlueprintComparator
from backend.validators.security import SecurityValidator

analyzer_bp = Blueprint('analyzer', __name__, url_prefix='/analyzer')

@analyzer_bp.route('/view/<int:project_id>', methods=['GET', 'POST'])
@login_required
def view_analyzer(project_id):
    project = Project.query.get_or_404(project_id)
    blueprint = ProjectBlueprint.query.filter_by(project_id=project.id).first()
    analysis = ProjectAnalysis.query.filter_by(project_id=project.id).first()

    if request.method == 'POST':
        project_path = request.form.get('project_path', '').strip()
        file_upload = request.files.get('project_zip')

        target_dir = None

        if file_upload and file_upload.filename.endswith('.zip'):
            filename = SecurityValidator.sanitize_string(file_upload.filename)
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], f"proj_{project.id}")
            os.makedirs(upload_dir, exist_ok=True)
            zip_path = os.path.join(upload_dir, filename)
            file_upload.save(zip_path)

            target_dir = os.path.join(upload_dir, 'extracted')
            os.makedirs(target_dir, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)

        elif project_path and os.path.exists(project_path):
            target_dir = project_path
        else:
            # Self-analysis fallback for testing workspace
            target_dir = current_app.config['BASE_DIR']

        if target_dir:
            dir_res = ProjectDirectoryAnalyzer.analyze_directory(target_dir)
            comp_res = BlueprintComparator.compare(blueprint, dir_res) if blueprint else {}

            if not analysis:
                analysis = ProjectAnalysis(project_id=project.id)
                db.session.add(analysis)

            analysis.project_path = target_dir
            analysis.files_detected = json.dumps(dir_res.get('files_detected', []))
            analysis.languages_detected = json.dumps(dir_res.get('languages_detected', []))
            analysis.frameworks_detected = json.dumps(dir_res.get('frameworks_detected', []))
            analysis.dependencies_detected = json.dumps(dir_res.get('dependencies_detected', []))
            analysis.routes_detected = json.dumps(dir_res.get('routes_detected', []))
            analysis.models_detected = json.dumps(dir_res.get('models_detected', []))
            analysis.tests_detected = json.dumps(dir_res.get('tests_detected', []))
            analysis.blueprint_comparison_json = json.dumps(comp_res.get('module_status', []))
            analysis.development_guidance_json = json.dumps({
                "progress_percentage": comp_res.get('progress_percentage', 0),
                "recommended_next_step": comp_res.get('recommended_next_step', ''),
                "has_auth": comp_res.get('has_auth', False),
                "has_database": comp_res.get('has_database', False),
                "has_tests": comp_res.get('has_tests', False)
            })

            # Update project overall status
            project.progress_percentage = comp_res.get('progress_percentage', project.progress_percentage)
            project.status = 'Development'

            # Log activity
            log = ActivityLog(user_id=current_user.id, action='Analyzed Project Code', details=f'Analyzed code at {target_dir}')
            db.session.add(log)
            db.session.commit()

            flash('Project directory analysis and Blueprint comparison completed!', 'success')
            return redirect(url_for('analyzer.view_analyzer', project_id=project.id))

    files = json.loads(analysis.files_detected or '[]') if analysis else []
    languages = json.loads(analysis.languages_detected or '[]') if analysis else []
    frameworks = json.loads(analysis.frameworks_detected or '[]') if analysis else []
    routes = json.loads(analysis.routes_detected or '[]') if analysis else []
    models = json.loads(analysis.models_detected or '[]') if analysis else []
    tests = json.loads(analysis.tests_detected or '[]') if analysis else []
    comparison = json.loads(analysis.blueprint_comparison_json or '[]') if analysis else []
    guidance = json.loads(analysis.development_guidance_json or '{}') if analysis else {}

    return render_template(
        'analyzer/view.html',
        project=project,
        analysis=analysis,
        files=files,
        languages=languages,
        frameworks=frameworks,
        routes=routes,
        models=models,
        tests=tests,
        comparison=comparison,
        guidance=guidance
    )
