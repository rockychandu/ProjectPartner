import json
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.models.models import db, Project, Roadmap, Milestone, Task
from backend.algorithms.generators import RoadmapGenerator

roadmap_bp = Blueprint('roadmap', __name__, url_prefix='/roadmap')

@roadmap_bp.route('/view/<int:project_id>')
@login_required
def view_roadmap(project_id):
    project = Project.query.get_or_404(project_id)
    roadmap = Roadmap.query.filter_by(project_id=project.id).first()
    tasks = Task.query.filter_by(project_id=project.id).all()

    if not roadmap:
        task_dicts = [{
            "id": t.id,
            "title": t.title,
            "module_name": t.module_name,
            "assignee_name": t.assignee_name
        } for t in tasks]

        rm_data = RoadmapGenerator.generate_roadmap(8, task_dicts)
        roadmap = Roadmap(
            project_id=project.id,
            total_weeks=rm_data["total_weeks"],
            timeline_data_json=json.dumps(rm_data["weeks"])
        )
        db.session.add(roadmap)
        db.session.flush()

        for w_data in rm_data["weeks"]:
            m = Milestone(
                roadmap_id=roadmap.id,
                title=w_data["title"],
                week_number=w_data["week"],
                deliverables=json.dumps(w_data["deliverables"]),
                is_completed=False
            )
            db.session.add(m)

        db.session.commit()

    weeks = json.loads(roadmap.timeline_data_json or '[]')
    milestones = Milestone.query.filter_by(roadmap_id=roadmap.id).order_by(Milestone.week_number).all()

    return render_template('roadmap/view.html', project=project, roadmap=roadmap, weeks=weeks, milestones=milestones)
