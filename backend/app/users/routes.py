import json
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from backend.models.models import db, StudentProfile, ActivityLog

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    student_prof = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not student_prof:
        student_prof = StudentProfile(user_id=current_user.id)
        db.session.add(student_prof)
        db.session.commit()

    if request.method == 'POST':
        languages = request.form.getlist('languages')
        technologies = request.form.getlist('technologies')
        skills = request.form.getlist('skills')
        domains = request.form.getlist('domains')
        available_time = int(request.form.get('available_time', 10))
        preferred_difficulty = request.form.get('preferred_difficulty', 'Intermediate')
        team_preference = request.form.get('team_preference', 'Team')
        previous_projects = request.form.get('previous_projects', '')

        student_prof.set_languages(languages)
        student_prof.set_technologies(technologies)
        student_prof.set_skills(skills)
        student_prof.set_domains(domains)
        student_prof.available_time_hours_per_week = available_time
        student_prof.preferred_difficulty = preferred_difficulty
        student_prof.team_preference = team_preference
        student_prof.previous_projects = previous_projects

        log = ActivityLog(user_id=current_user.id, action='Profile Update', details='Updated skills, interests, and availability.')
        db.session.add(log)
        db.session.commit()

        flash('Your profile details have been saved!', 'success')
        return redirect(url_for('projects.generator'))

    return render_template(
        'users/profile.html',
        profile=student_prof,
        languages=student_prof.get_languages(),
        technologies=student_prof.get_technologies(),
        skills=student_prof.get_skills(),
        domains=student_prof.get_domains()
    )


@users_bp.route('/settings')
@login_required
def settings():
    return render_template('users/settings.html')
