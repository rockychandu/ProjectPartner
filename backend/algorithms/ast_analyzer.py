import os
import ast
import json

class PythonASTAnalyzer:
    """
    Safely inspects Python files using Python AST module without executing code.
    Detects routes, classes, function definitions, database models, and unit tests.
    """

    @staticmethod
    def analyze_python_file(file_path):
        results = {
            "routes": [],
            "models": [],
            "functions": [],
            "classes": [],
            "imports": [],
            "tests": []
        }
        
        if not os.path.exists(file_path):
            return results

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)

            for node in ast.walk(tree):
                # Imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        results["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        results["imports"].append(node.module)

                # Class definitions (DB Models check)
                elif isinstance(node, ast.ClassDef):
                    results["classes"].append(node.name)
                    base_names = []
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            base_names.append(base.id)
                        elif isinstance(base, ast.Attribute):
                            base_names.append(base.attr)
                    if any(b in ["Model", "Base", "db.Model"] for b in base_names):
                        results["models"].append(node.name)

                # Function definitions (Routes & Tests check)
                elif isinstance(node, ast.FunctionDef):
                    results["functions"].append(node.name)
                    if node.name.startswith("test_"):
                        results["tests"].append(node.name)

                    # Check decorators for Flask routes (@app.route, @bp.route, etc.)
                    for decorator in node.decorator_list:
                        decorator_attr = None
                        if isinstance(decorator, ast.Call):
                            if isinstance(decorator.func, ast.Attribute):
                                decorator_attr = decorator.func.attr
                            elif isinstance(decorator.func, ast.Name):
                                decorator_attr = decorator.func.id
                        elif isinstance(decorator, ast.Attribute):
                            decorator_attr = decorator.attr
                        elif isinstance(decorator, ast.Name):
                            decorator_attr = decorator.id

                        if decorator_attr == "route":
                            results["routes"].append(node.name)

        except Exception as e:
            results["error"] = str(e)

        return results


class ProjectDirectoryAnalyzer:
    @staticmethod
    def analyze_directory(root_path):
        analysis = {
            "files_detected": [],
            "languages_detected": set(),
            "frameworks_detected": set(),
            "dependencies_detected": [],
            "routes_detected": [],
            "models_detected": [],
            "tests_detected": [],
            "has_auth": False,
            "has_database": False,
            "has_tests": False
        }

        if not os.path.exists(root_path):
            return analysis

        for dirpath, dirnames, filenames in os.walk(root_path):
            dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in ['venv', '__pycache__', 'node_modules']]
            
            for filename in filenames:
                rel_file = os.path.relpath(os.path.join(dirpath, filename), root_path)
                analysis["files_detected"].append(rel_file)

                ext = os.path.splitext(filename)[1].lower()
                if ext == ".py":
                    analysis["languages_detected"].add("Python")
                    full_p = os.path.join(dirpath, filename)
                    ast_res = PythonASTAnalyzer.analyze_python_file(full_p)
                    
                    analysis["routes_detected"].extend(ast_res["routes"])
                    analysis["models_detected"].extend(ast_res["models"])
                    analysis["tests_detected"].extend(ast_res["tests"])
                    
                    for imp in ast_res["imports"]:
                        if "flask" in imp.lower():
                            analysis["frameworks_detected"].add("Flask")
                        if "django" in imp.lower():
                            analysis["frameworks_detected"].add("Django")
                        if "sklearn" in imp.lower() or "scikit" in imp.lower():
                            analysis["frameworks_detected"].add("Scikit-Learn")
                        if "cv2" in imp.lower() or "opencv" in imp.lower():
                            analysis["frameworks_detected"].add("OpenCV")
                        if "pytest" in imp.lower() or "unittest" in imp.lower():
                            analysis["frameworks_detected"].add("Pytest/Unittest")

                    if "auth" in filename.lower() or any("login" in r for r in ast_res["routes"]):
                        analysis["has_auth"] = True

                elif ext in [".html", ".jinja", ".jinja2"]:
                    analysis["languages_detected"].add("HTML")
                elif ext == ".css":
                    analysis["languages_detected"].add("CSS")
                elif ext == ".js":
                    analysis["languages_detected"].add("JavaScript")
                elif ext in [".sql", ".sqlite", ".db"]:
                    analysis["languages_detected"].add("SQL")
                    analysis["has_database"] = True

                if filename.lower() == "requirements.txt":
                    full_p = os.path.join(dirpath, filename)
                    try:
                        with open(full_p, "r", encoding="utf-8", errors="ignore") as rf:
                            lines = [l.strip() for l in rf.readlines() if l.strip() and not l.startswith('#')]
                            analysis["dependencies_detected"].extend(lines)
                    except Exception:
                        pass

        if len(analysis["models_detected"]) > 0 or "SQL" in analysis["languages_detected"]:
            analysis["has_database"] = True

        if len(analysis["tests_detected"]) > 0 or any("test" in f.lower() for f in analysis["files_detected"]):
            analysis["has_tests"] = True

        analysis["languages_detected"] = list(analysis["languages_detected"])
        analysis["frameworks_detected"] = list(analysis["frameworks_detected"])
        return analysis


class BlueprintComparator:
    @staticmethod
    def compare(blueprint, project_analysis):
        blueprint_modules = json.loads(blueprint.modules_json or '[]') if hasattr(blueprint, 'modules_json') else blueprint.get('modules', [])
        
        detected_files = project_analysis.get('files_detected', [])
        detected_routes = project_analysis.get('routes_detected', [])
        detected_models = project_analysis.get('models_detected', [])
        has_tests = project_analysis.get('has_tests', False)
        has_auth = project_analysis.get('has_auth', False)
        has_database = project_analysis.get('has_database', False)

        module_status = []
        completed_count = 0

        for mod in blueprint_modules:
            mod_name = mod if isinstance(mod, str) else mod.get('name', '')
            lower_mod = mod_name.lower()

            status = "Missing"
            confidence = "High Confidence"

            if "auth" in lower_mod or "user" in lower_mod or "login" in lower_mod:
                if has_auth:
                    status = "Completed"
                else:
                    status = "Missing"
            elif "database" in lower_mod or "model" in lower_mod or "store" in lower_mod:
                if has_database or len(detected_models) > 0:
                    status = "Completed"
                else:
                    status = "Missing"
            elif "test" in lower_mod or "qa" in lower_mod:
                if has_tests:
                    status = "Completed"
                else:
                    status = "Missing"
            else:
                if any(lower_mod in f.lower() for f in detected_files) or any(lower_mod in r.lower() for r in detected_routes):
                    status = "In Progress"
                    confidence = "Medium Confidence"
                elif len(detected_files) > 2:
                    status = "In Progress"
                    confidence = "Medium Confidence"

            if status == "Completed":
                completed_count += 1

            module_status.append({
                "module_name": mod_name,
                "status": status,
                "confidence": confidence
            })

        total_mods = max(len(blueprint_modules), 1)
        progress_pct = int((completed_count / total_mods) * 100)

        recommended_step = "Continue building core functional modules."
        if not has_database and any("database" in m["module_name"].lower() for m in module_status):
            recommended_step = "Define database models and setup database connection."
        elif not has_auth and any("auth" in m["module_name"].lower() for m in module_status):
            recommended_step = "Implement User Authentication & Login handling."
        elif not has_tests:
            recommended_step = "Create automated unit tests for core module verification."
        elif progress_pct >= 80:
            recommended_step = "Generate system documentation and prepare presentation deck."

        return {
            "progress_percentage": progress_pct,
            "module_status": module_status,
            "has_auth": has_auth,
            "has_database": has_database,
            "has_tests": has_tests,
            "recommended_next_step": recommended_step
        }
