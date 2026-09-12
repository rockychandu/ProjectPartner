import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    college = db.Column(db.String(150), nullable=True)
    branch = db.Column(db.String(100), nullable=True)
    year = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    projects = db.relationship('Project', backref='user', cascade="all, delete-orphan")
    teams = db.relationship('TeamMember', backref='user', cascade="all, delete-orphan")
    activity_logs = db.relationship('ActivityLog', backref='user', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "college": self.college,
            "branch": self.branch,
            "year": self.year,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    programming_languages = db.Column(db.Text, default='[]')
    technologies = db.Column(db.Text, default='[]')
    skills = db.Column(db.Text, default='[]')
    skill_proficiency = db.Column(db.Text, default='{}')
    domains_of_interest = db.Column(db.Text, default='[]')
    previous_projects = db.Column(db.Text, default='')
    available_time_hours_per_week = db.Column(db.Integer, default=10)
    preferred_difficulty = db.Column(db.String(50), default='Intermediate')
    team_preference = db.Column(db.String(50), default='Team')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_languages(self):
        return json.loads(self.programming_languages or '[]')
    
    def set_languages(self, langs):
        self.programming_languages = json.dumps(langs)

    def get_technologies(self):
        return json.loads(self.technologies or '[]')

    def set_technologies(self, techs):
        self.technologies = json.dumps(techs)

    def get_skills(self):
        return json.loads(self.skills or '[]')

    def set_skills(self, sk):
        self.skills = json.dumps(sk)

    def get_domains(self):
        return json.loads(self.domains_of_interest or '[]')

    def set_domains(self, doms):
        self.domains_of_interest = json.dumps(doms)

    def get_proficiency(self):
        return json.loads(self.skill_proficiency or '{}')

    def set_proficiency(self, prof):
        self.skill_proficiency = json.dumps(prof)


class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=True)


class Domain(db.Model):
    __tablename__ = 'domains'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)


class Technology(db.Model):
    __tablename__ = 'technologies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=True)


class ProgrammingLanguage(db.Model):
    __tablename__ = 'programming_languages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class Problem(db.Model):
    __tablename__ = 'problems'
    id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.Integer, db.ForeignKey('domains.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    target_users = db.Column(db.Text, nullable=True)


class KnowledgeItem(db.Model):
    __tablename__ = 'knowledge_items'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    key_name = db.Column(db.String(150), nullable=False)
    content_json = db.Column(db.Text, nullable=False)


class ProjectIdea(db.Model):
    __tablename__ = 'project_ideas'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    domain = db.Column(db.String(100), nullable=False)
    problem = db.Column(db.Text, nullable=False)
    target_users = db.Column(db.Text, nullable=True)
    solution = db.Column(db.Text, nullable=False)
    core_features = db.Column(db.Text, nullable=False)
    technology_stack = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    estimated_duration_weeks = db.Column(db.Integer, default=8)
    duration_value = db.Column(db.Integer, default=8)
    duration_unit = db.Column(db.String(20), default='Weeks') # Hours, Days, Weeks, Months
    team_size = db.Column(db.Integer, nullable=False)
    innovation_summary = db.Column(db.Text, nullable=True)
    dataset_required = db.Column(db.String(200), nullable=True)
    hardware_required = db.Column(db.String(200), nullable=True)
    api_required = db.Column(db.Boolean, default=False)
    implementation_complexity = db.Column(db.String(50), default='Medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_features(self):
        return json.loads(self.core_features or '[]')

    def get_tech_stack(self):
        return json.loads(self.technology_stack or '[]')

    def get_formatted_duration(self):
        val = self.duration_value or self.estimated_duration_weeks or 8
        unit = self.duration_unit or 'Weeks'
        return f"{val} {unit}"


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    idea_id = db.Column(db.Integer, db.ForeignKey('project_ideas.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    domain = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='Selection')
    progress_percentage = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    blueprint = db.relationship('ProjectBlueprint', backref='project', uselist=False, cascade="all, delete-orphan")
    modules = db.relationship('ProjectModule', backref='project', cascade="all, delete-orphan")
    teams = db.relationship('Team', backref='project', cascade="all, delete-orphan")
    tasks = db.relationship('Task', backref='project', cascade="all, delete-orphan")
    roadmap = db.relationship('Roadmap', backref='project', uselist=False, cascade="all, delete-orphan")
    analysis = db.relationship('ProjectAnalysis', backref='project', uselist=False, cascade="all, delete-orphan")
    documentation = db.relationship('Documentation', backref='project', uselist=False, cascade="all, delete-orphan")
    presentation = db.relationship('Presentation', backref='project', uselist=False, cascade="all, delete-orphan")
    resume_entries = db.relationship('ResumeEntry', backref='project', cascade="all, delete-orphan")


class ProjectBlueprint(db.Model):
    __tablename__ = 'project_blueprints'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, unique=True)
    overview = db.Column(db.Text, nullable=False)
    problem_statement = db.Column(db.Text, nullable=False)
    objectives = db.Column(db.Text, nullable=False)
    target_users = db.Column(db.Text, nullable=False)
    core_features = db.Column(db.Text, nullable=False)
    modules_json = db.Column(db.Text, nullable=False)
    tech_stack_json = db.Column(db.Text, nullable=False)
    software_requirements = db.Column(db.Text, nullable=True)
    hardware_requirements = db.Column(db.Text, nullable=True)
    database_requirements = db.Column(db.Text, nullable=True)
    architecture_overview = db.Column(db.Text, nullable=True)
    data_flow = db.Column(db.Text, nullable=True)
    ml_methodology = db.Column(db.Text, nullable=True)
    folder_structure = db.Column(db.Text, nullable=True)
    development_phases = db.Column(db.Text, nullable=True)
    testing_requirements = db.Column(db.Text, nullable=True)
    deployment_requirements = db.Column(db.Text, nullable=True)
    future_scope = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ProjectModule(db.Model):
    __tablename__ = 'project_modules'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='Pending')
    order_index = db.Column(db.Integer, default=0)


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship('TeamMember', backref='team', cascade="all, delete-orphan")


class TeamMember(db.Model):
    __tablename__ = 'team_members'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    member_name = db.Column(db.String(120), nullable=False)
    skills = db.Column(db.Text, default='[]')
    experience = db.Column(db.String(100), default='Intermediate')
    preferred_role = db.Column(db.String(100), nullable=True)
    assigned_role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='SET NULL'), nullable=True)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    required_skills = db.Column(db.Text, default='[]')


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    module_name = db.Column(db.String(150), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    assignee_name = db.Column(db.String(120), nullable=True)
    priority = db.Column(db.String(20), default='Medium')
    estimated_hours = db.Column(db.Integer, default=5)
    deadline_day = db.Column(db.Integer, default=1)
    required_skill = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), default='Pending')
    subtasks_json = db.Column(db.Text, default='[]')

    dependencies = db.relationship('TaskDependency', foreign_keys='TaskDependency.task_id', backref='task', cascade="all, delete-orphan")


class TaskDependency(db.Model):
    __tablename__ = 'task_dependencies'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    depends_on_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)


class Roadmap(db.Model):
    __tablename__ = 'roadmaps'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, unique=True)
    total_weeks = db.Column(db.Integer, default=8)
    timeline_data_json = db.Column(db.Text, nullable=False)

    milestones = db.relationship('Milestone', backref='roadmap', cascade="all, delete-orphan")


class Milestone(db.Model):
    __tablename__ = 'milestones'
    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey('roadmaps.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    deliverables = db.Column(db.Text, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)


class ProjectAnalysis(db.Model):
    __tablename__ = 'project_analysis'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, unique=True)
    project_path = db.Column(db.String(300), nullable=True)
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    files_detected = db.Column(db.Text, default='[]')
    languages_detected = db.Column(db.Text, default='[]')
    frameworks_detected = db.Column(db.Text, default='[]')
    dependencies_detected = db.Column(db.Text, default='[]')
    routes_detected = db.Column(db.Text, default='[]')
    models_detected = db.Column(db.Text, default='[]')
    tests_detected = db.Column(db.Text, default='[]')
    blueprint_comparison_json = db.Column(db.Text, default='{}')
    development_guidance_json = db.Column(db.Text, default='{}')


class Documentation(db.Model):
    __tablename__ = 'documentation'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, unique=True)
    abstract = db.Column(db.Text, nullable=False)
    srs_content = db.Column(db.Text, nullable=False)
    readme_content = db.Column(db.Text, nullable=False)
    full_report_content = db.Column(db.Text, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)


class Presentation(db.Model):
    __tablename__ = 'presentations'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, unique=True)
    slides_json = db.Column(db.Text, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)


class ResumeEntry(db.Model):
    __tablename__ = 'resume_entries'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    bullet_point = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='Impact')


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    action = db.Column(db.String(150), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
