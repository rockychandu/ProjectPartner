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


@analyzer_bp.route('/measurement/<int:project_id>', methods=['GET'])
@login_required
def view_measurement(project_id):
    """
    CodePlex Measurement Route.
    Dedicated interface for running CodeMetrix measure.py evaluation and inspecting repository quality metrics.
    """
    project = Project.query.get_or_404(project_id)
    return render_template('analyzer/measurement.html', project=project)


@analyzer_bp.route('/api/run-checks', methods=['POST'])
@analyzer_bp.route('/run-checks', methods=['POST'])
def api_run_checks():
    """
    TrainPlex Run Checks & measure.py Pipeline API.
    Handles ZIP upload (up to 100 MB), extracts archive, executes measure.py as a subprocess,
    captures exit code, stdout, stderr, and ALWAYS returns valid JSON for both success and failure.
    """
    import sys
    import subprocess
    import tempfile
    import traceback

    try:
        file_upload = request.files.get('project_zip') or request.files.get('file') or request.files.get('zip_file')
        repo_url = request.form.get('repo_url') or request.form.get('github_url')
        project_path = request.form.get('project_path')

        temp_dir_obj = tempfile.TemporaryDirectory()
        target_dir = temp_dir_obj.name

        if file_upload and file_upload.filename.endswith('.zip'):
            filename = SecurityValidator.sanitize_string(file_upload.filename)
            zip_path = os.path.join(target_dir, 'uploaded_project.zip')
            file_upload.save(zip_path)

            extract_dir = os.path.join(target_dir, 'extracted')
            os.makedirs(extract_dir, exist_ok=True)
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                target_dir = extract_dir
            except zipfile.BadZipFile as e:
                return jsonify({
                    "success": False,
                    "error": f"Invalid or corrupted ZIP archive: {str(e)}",
                    "exit_code": 1,
                    "stdout": "",
                    "stderr": traceback.format_exc()
                }), 400
        elif project_path and os.path.exists(project_path):
            target_dir = project_path
        else:
            target_dir = current_app.config['BASE_DIR']

        # Determine path to measure.py
        base_dir = current_app.config['BASE_DIR']
        measure_script = os.path.join(base_dir, 'measure.py')
        out_dir = os.path.join(target_dir, 'measure_output')
        os.makedirs(out_dir, exist_ok=True)

        python_exec = sys.executable or 'python'
        cmd = [python_exec, measure_script, target_dir, '--out', out_dir, '--no-llm', '--build', 'none']

        stdout = ""
        stderr = ""
        exit_code = 0

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                errors='replace'
            )
            stdout = res.stdout
            stderr = res.stderr
            exit_code = res.returncode
        except subprocess.TimeoutExpired as e:
            stdout = e.stdout or ""
            stderr = e.stderr or "Execution timed out after 300 seconds."
            return jsonify({
                "success": False,
                "error": "measure.py execution timed out (limit: 300 seconds)",
                "exit_code": -1,
                "stdout": stdout,
                "stderr": stderr
            }), 500
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Subprocess execution failure: {str(e)}",
                "exit_code": -1,
                "stdout": "",
                "stderr": traceback.format_exc()
            }), 500

        # Read measurement.json if available
        measurement_json_path = os.path.join(out_dir, 'measurement.json')
        measurement_data = {}
        if os.path.exists(measurement_json_path):
            try:
                with open(measurement_json_path, 'r', encoding='utf-8') as f:
                    measurement_data = json.load(f)
            except Exception:
                pass

        if exit_code != 0:
            return jsonify({
                "success": False,
                "error": f"measure.py failed with exit code {exit_code}",
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "measurement": measurement_data
            }), 400

        return jsonify({
            "success": True,
            "exit_code": exit_code,
            "message": "CodeMetrix checks and measure.py completed successfully",
            "stdout": stdout,
            "stderr": stderr,
            "total_loc": measurement_data.get('tree', {}).get('total_loc', 0),
            "total_files": measurement_data.get('tree', {}).get('total_source_files', 0),
            "primary_language": measurement_data.get('tree', {}).get('primary_language', 'Python'),
            "measurement": measurement_data
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unhandled Server Exception: {str(e)}",
            "exit_code": -1,
            "stdout": "",
            "stderr": traceback.format_exc()
        }), 500

