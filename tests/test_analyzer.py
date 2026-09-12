import os
import tempfile
from backend.algorithms.ast_analyzer import PythonASTAnalyzer, ProjectDirectoryAnalyzer, BlueprintComparator

def test_ast_python_analyzer():
    tf = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
    try:
        tf.write("""
from flask import Flask
app = Flask(__name__)

class User(db.Model):
    id = db.Column(db.Integer)

@app.route('/login')
def login():
    return 'login'

def test_user_login():
    assert True
""")
        tf.close()

        ast_res = PythonASTAnalyzer.analyze_python_file(tf.name)
        assert "flask" in [i.lower() for i in ast_res["imports"]]
        assert "User" in ast_res["models"]
        assert "login" in ast_res["routes"]
        assert "test_user_login" in ast_res["tests"]
    finally:
        if os.path.exists(tf.name):
            os.remove(tf.name)

def test_blueprint_comparator():
    blueprint = type('obj', (object,), {
        'modules_json': '["Auth Module", "Database Module", "QA Module"]'
    })
    analysis = {
        'files_detected': ['app.py', 'models.py'],
        'routes_detected': ['login'],
        'models_detected': ['User'],
        'has_auth': True,
        'has_database': True,
        'has_tests': False
    }

    comp = BlueprintComparator.compare(blueprint, analysis)
    assert comp['has_auth'] is True
    assert comp['has_database'] is True
    assert comp['has_tests'] is False
    assert "unit tests" in comp['recommended_next_step'].lower()
