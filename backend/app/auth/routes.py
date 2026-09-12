from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from backend.models.models import db, User, StudentProfile, ActivityLog
from backend.validators.security import SecurityValidator

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = SecurityValidator.sanitize_string(request.form.get('name'))
        email = SecurityValidator.sanitize_string(request.form.get('email'))
        password = request.form.get('password')
        college = SecurityValidator.sanitize_string(request.form.get('college'))
        branch = SecurityValidator.sanitize_string(request.form.get('branch'))
        year = SecurityValidator.sanitize_string(request.form.get('year'))

        if not name or not email or not password:
            flash('Name, email, and password are required.', 'danger')
            return render_template('auth/register.html')

        if not SecurityValidator.validate_email(email):
            flash('Invalid email address format.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email address is already registered.', 'warning')
            return render_template('auth/register.html')

        user = User(name=name, email=email, college=college, branch=branch, year=year)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        # Create initial student profile
        profile = StudentProfile(user_id=user.id)
        db.session.add(profile)

        # Log activity
        log = ActivityLog(user_id=user.id, action='Account Registration', details='Registered new student account.')
        db.session.add(log)
        
        db.session.commit()

        login_user(user)
        flash('Registration successful! Please complete your student profile.', 'success')
        return redirect(url_for('users.profile', splash='1'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = SecurityValidator.sanitize_string(request.form.get('email'))
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        login_user(user)
        
        # Log activity
        log = ActivityLog(user_id=user.id, action='Account Login', details='Logged into platform.')
        db.session.add(log)
        db.session.commit()

        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(url_for('workspace.dashboard', splash='1'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login', splash='1'))
