import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from backend.models.models import db, User
from backend.app.config import Config

def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder=os.path.join(config_class.BASE_DIR, 'frontend', 'templates'),
        static_folder=os.path.join(config_class.BASE_DIR, 'frontend', 'static')
    )
    app.config.from_object(config_class)

    # Ensure upload and database folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db_dir = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    # Initialize Extensions
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from backend.app.auth.routes import auth_bp
    from backend.app.users.routes import users_bp
    from backend.app.projects.routes import projects_bp
    from backend.app.blueprint.routes import blueprint_bp
    from backend.app.teams.routes import teams_bp
    from backend.app.tasks.routes import tasks_bp
    from backend.app.roadmap.routes import roadmap_bp
    from backend.app.mentor.routes import mentor_bp
    from backend.app.analyzer.routes import analyzer_bp
    from backend.app.documentation.routes import documentation_bp
    from backend.app.workspace.routes import workspace_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(blueprint_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(mentor_bp)
    app.register_blueprint(analyzer_bp)
    app.register_blueprint(documentation_bp)
    app.register_blueprint(workspace_bp)

    @app.route('/')
    def index():
        return render_template('landing.html')

    with app.app_context():
        db.create_all()

    return app
