import json
from flask import Blueprint, request, render_template, jsonify
from flask_login import login_required, current_user
from backend.models.models import Project, ProjectBlueprint, ProjectAnalysis, Task
from backend.algorithms.generators import ProjectMentorEngine

mentor_bp = Blueprint('mentor', __name__, url_prefix='/mentor')

@mentor_bp.route('/chat/<int:project_id>', methods=['GET', 'POST'])
@login_required
def chat(project_id):
    project = Project.query.get_or_404(project_id)
    blueprint = ProjectBlueprint.query.filter_by(project_id=project.id).first()
    analysis = ProjectAnalysis.query.filter_by(project_id=project.id).first()
    tasks = Task.query.filter_by(project_id=project.id).all()

    if request.method == 'POST':
        data = request.get_json() or {}
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({"response": "Please enter a valid question regarding your project."})

        answer = ProjectMentorEngine.answer_query(user_query, project, blueprint, analysis, tasks)
        return jsonify({"response": answer})

    return render_template('mentor/chat.html', project=project)
