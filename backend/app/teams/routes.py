import json
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.models.models import db, Project, Team, TeamMember, Role, ActivityLog

teams_bp = Blueprint('teams', __name__, url_prefix='/teams')

@teams_bp.route('/manage/<int:project_id>', methods=['GET', 'POST'])
@login_required
def manage_team(project_id):
    project = Project.query.get_or_404(project_id)
    team = Team.query.filter_by(project_id=project.id).first()

    if not team:
        team = Team(project_id=project.id, name=f"{project.title} Team")
        db.session.add(team)
        db.session.flush()
        
        # Add current student as lead
        lead_member = TeamMember(
            team_id=team.id,
            user_id=current_user.id,
            member_name=current_user.name,
            skills=json.dumps(["Python", "Flask", "SQL"]),
            experience="Intermediate",
            preferred_role="Full-Stack Lead"
        )
        db.session.add(lead_member)
        db.session.commit()

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_member':
            name = request.form.get('member_name')
            skills = request.form.get('skills', '').split(',')
            skills = [s.strip() for s in skills if s.strip()]
            experience = request.form.get('experience', 'Intermediate')
            pref_role = request.form.get('preferred_role', 'Backend')

            member = TeamMember(
                team_id=team.id,
                member_name=name,
                skills=json.dumps(skills),
                experience=experience,
                preferred_role=pref_role
            )
            db.session.add(member)
            db.session.commit()
            flash(f'Added team member "{name}"!', 'success')

        elif action == 'allocate_roles':
            # Smart Role Allocation Algorithm
            members = TeamMember.query.filter_by(team_id=team.id).all()
            roles_def = [
                {"title": "Full-Stack Lead", "req": ["Python", "Flask", "SQL"]},
                {"title": "Backend & Database Engineer", "req": ["Python", "SQLite", "PostgreSQL", "SQL"]},
                {"title": "Frontend & UI Engineer", "req": ["HTML", "CSS", "JavaScript", "Jinja2"]},
                {"title": "ML & Algorithm Specialist", "req": ["Python", "Scikit-Learn", "OpenCV", "AST"]},
                {"title": "QA & Testing Specialist", "req": ["Pytest", "Testing", "QA", "Unittest"]}
            ]

            for idx, m in enumerate(members):
                m_skills = json.loads(m.skills or '[]')
                assigned = False
                for r in roles_def:
                    if any(s in m_skills for s in r["req"]) or m.preferred_role == r["title"]:
                        m.preferred_role = r["title"]
                        assigned = True
                        break
                if not assigned:
                    m.preferred_role = roles_def[idx % len(roles_def)]["title"]

            db.session.commit()
            flash('Team roles successfully allocated based on skills and preferences!', 'success')
            return redirect(url_for('tasks.view_tasks', project_id=project.id))

    members = TeamMember.query.filter_by(team_id=team.id).all()
    return render_template('teams/manage.html', project=project, team=team, members=members)
