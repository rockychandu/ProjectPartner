import json
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from backend.models.models import db, Project, ProjectBlueprint, Team, TeamMember, Task, TaskDependency
from backend.algorithms.generators import TaskGraphGenerator

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@tasks_bp.route('/view/<int:project_id>', methods=['GET', 'POST'])
@login_required
def view_tasks(project_id):
    project = Project.query.get_or_404(project_id)
    blueprint = ProjectBlueprint.query.filter_by(project_id=project.id).first()
    team = Team.query.filter_by(project_id=project.id).first()
    members = TeamMember.query.filter_by(team_id=team.id).all() if team else []

    existing_tasks = Task.query.filter_by(project_id=project.id).order_by(Task.id).all()

    # Generate tasks if none exist
    if not existing_tasks and blueprint:
        from backend.models.models import ProjectIdea
        idea = ProjectIdea.query.get(project.idea_id) if project.idea_id else None
        bp_dict = {
            "modules": json.loads(blueprint.modules_json or '[]')
        }
        task_list = TaskGraphGenerator.generate_tasks(project, bp_dict, members, idea)

        task_id_map = {}
        for t_data in task_list:
            t = Task(
                project_id=project.id,
                module_name=t_data["module_name"],
                title=t_data["title"],
                description=t_data["description"],
                assignee_name=t_data["assignee_name"],
                priority=t_data["priority"],
                estimated_hours=t_data["estimated_hours"],
                deadline_day=t_data["deadline_day"],
                required_skill=t_data["required_skill"],
                status="Pending"
            )
            db.session.add(t)
            db.session.flush()
            task_id_map[t_data["id"]] = t.id

            # Dependencies
            for dep_old_id in t_data.get("depends_on", []):
                if dep_old_id in task_id_map:
                    dep = TaskDependency(task_id=t.id, depends_on_task_id=task_id_map[dep_old_id])
                    db.session.add(dep)

        db.session.commit()
        existing_tasks = Task.query.filter_by(project_id=project.id).order_by(Task.id).all()

    if request.method == 'POST':
        task_id = request.form.get('task_id')
        new_status = request.form.get('status')
        task = Task.query.get(task_id)
        if task and task.project_id == project.id:
            task.status = new_status
            
            # Recalculate project overall progress %
            all_tasks = Task.query.filter_by(project_id=project.id).all()
            completed = sum(1 for t in all_tasks if t.status == 'Completed')
            project.progress_percentage = int((completed / max(len(all_tasks), 1)) * 100)
            
            db.session.commit()
            flash(f'Updated task "{task.title}" status to {new_status}.', 'success')
            return redirect(url_for('tasks.view_tasks', project_id=project.id))

    return render_template('tasks/view.html', project=project, tasks=existing_tasks, members=members)
