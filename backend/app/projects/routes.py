import json
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from backend.models.models import db, ProjectIdea, Project, StudentProfile, ActivityLog
from backend.algorithms.generators import CombinatorialProjectGenerator, BlueprintGenerator
from backend.algorithms.nlp_engine import RecommendationEngine

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')
generator_engine = CombinatorialProjectGenerator()

@projects_bp.route('/generator', methods=['GET', 'POST'])
@login_required
def generator():
    student_prof = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        domain = request.form.get('domain', 'All')
        technology = request.form.get('technology', 'All')
        difficulty = request.form.get('difficulty', 'All')
        duration_val = int(request.form.get('duration_value', 8))
        duration_unit = request.form.get('duration_unit', 'Weeks')
        team_size = int(request.form.get('team_size', 3))
        api_allowed = request.form.get('api_allowed') == 'true'
        hardware = request.form.get('hardware', 'Not Required')

        filters = {
            "domain": domain,
            "technology": technology,
            "difficulty": difficulty,
            "duration": duration_val,
            "duration_value": duration_val,
            "duration_unit": duration_unit,
            "team_size": team_size,
            "api_allowed": api_allowed,
            "hardware_required": hardware
        }

        existing_ideas_db = ProjectIdea.query.all()
        existing_ideas = [
            {"title": i.title, "problem": i.problem, "solution": i.solution}
            for i in existing_ideas_db
        ]

        candidates = generator_engine.generate_candidates(filters, existing_ideas)

        idea_models = []
        for cand in candidates:
            idea = ProjectIdea.query.filter_by(title=cand.get('title')).first()
            if not idea:
                idea = ProjectIdea(
                    title=cand.get('title'),
                    domain=cand.get('domain'),
                    problem=cand.get('problem'),
                    target_users=", ".join(cand.get('target_users', [])),
                    solution=cand.get('solution'),
                    core_features=json.dumps(cand.get('core_features', [])),
                    technology_stack=json.dumps(cand.get('technology_stack', [])),
                    difficulty=cand.get('difficulty', 'Intermediate'),
                    estimated_duration_weeks=cand.get('estimated_duration_weeks', duration_val),
                    duration_value=cand.get('duration_value', duration_val),
                    duration_unit=cand.get('duration_unit', duration_unit),
                    team_size=cand.get('team_size', team_size),
                    innovation_summary=cand.get('innovation', ''),
                    dataset_required=cand.get('dataset', ''),
                    hardware_required=cand.get('hardware', 'Not Required'),
                    api_required=cand.get('api_required', False),
                    implementation_complexity=cand.get('complexity', 'Medium')
                )
                db.session.add(idea)
                db.session.flush()
            idea_models.append(idea)

        db.session.commit()

        if student_prof:
            ranked_results = RecommendationEngine.rank_projects(student_prof, idea_models)
        else:
            ranked_results = [{"project": i, "overall_match": 85.0, "breakdown": {}} for i in idea_models]

        return render_template('projects/results.html', results=ranked_results, filters=filters)

    return render_template('projects/generator.html', profile=student_prof)


@projects_bp.route('/select/<int:idea_id>', methods=['POST'])
@login_required
def select_project(idea_id):
    idea = ProjectIdea.query.get_or_404(idea_id)

    project = Project(
        user_id=current_user.id,
        idea_id=idea.id,
        title=idea.title,
        domain=idea.domain,
        status='Blueprint',
        progress_percentage=10
    )
    db.session.add(project)
    db.session.flush()

    bp_data = BlueprintGenerator.generate_blueprint(idea)
    from backend.models.models import ProjectBlueprint
    blueprint = ProjectBlueprint(
        project_id=project.id,
        overview=bp_data['overview'],
        problem_statement=bp_data['problem_statement'],
        objectives=json.dumps(bp_data['objectives']),
        target_users=bp_data['target_users'],
        core_features=json.dumps(bp_data['core_features']),
        modules_json=json.dumps(bp_data['modules']),
        tech_stack_json=json.dumps(bp_data['tech_stack']),
        software_requirements=json.dumps(bp_data['software_requirements']),
        hardware_requirements=bp_data['hardware_requirements'],
        database_requirements=bp_data['database_requirements'],
        architecture_overview=bp_data['architecture_overview'],
        data_flow=bp_data['data_flow'],
        ml_methodology=bp_data['ml_methodology'],
        folder_structure=bp_data['folder_structure'],
        development_phases=json.dumps(bp_data['development_phases']),
        testing_requirements=bp_data['testing_requirements'],
        deployment_requirements=bp_data['deployment_requirements'],
        future_scope=bp_data['future_scope']
    )
    db.session.add(blueprint)

    log = ActivityLog(user_id=current_user.id, action='Selected Project', details=f'Selected project: {project.title}')
    db.session.add(log)
    db.session.commit()

    flash(f'Project "{project.title}" selected! Project Blueprint created.', 'success')
    return redirect(url_for('blueprint.view_blueprint', project_id=project.id))


@projects_bp.route('/details/<int:project_id>')
@login_required
def details(project_id):
    project = Project.query.get_or_404(project_id)
    idea = ProjectIdea.query.get(project.idea_id) if project.idea_id else None
    return render_template('projects/details.html', project=project, idea=idea)


@projects_bp.route('/compare')
@login_required
def compare():
    ideas = ProjectIdea.query.order_by(ProjectIdea.created_at.desc()).limit(3).all()
    return render_template('projects/compare.html', ideas=ideas)
