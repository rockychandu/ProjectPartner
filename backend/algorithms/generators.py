import os
import json
from datetime import datetime
from backend.algorithms.nlp_engine import LocalNLPEngine

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'knowledge')

def load_knowledge_file(filename):
    path = os.path.join(KNOWLEDGE_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

class CombinatorialProjectGenerator:
    def __init__(self):
        self.domains = load_knowledge_file('domains.json')
        self.problems = load_knowledge_file('problems.json')
        self.technologies = load_knowledge_file('technologies.json')
        self.templates = load_knowledge_file('project_templates.json')
        self.nlp_engine = LocalNLPEngine()

    def generate_candidates(self, filters, existing_ideas=None):
        if existing_ideas is None:
            existing_ideas = []

        domain_filter = filters.get('domain', 'All')
        tech_filter = filters.get('technology', 'All')
        difficulty_filter = filters.get('difficulty', 'All')
        duration_val = int(filters.get('duration_value', filters.get('duration', 8)))
        duration_unit = filters.get('duration_unit', 'Weeks')
        team_size_filter = int(filters.get('team_size', 3))
        api_filter = filters.get('api_allowed', True)
        hardware_filter = filters.get('hardware_required', 'Not Required')

        results = []

        for tpl in self.templates:
            if domain_filter != 'All' and tpl.get('domain') != domain_filter:
                continue
            if difficulty_filter != 'All' and tpl.get('difficulty') != difficulty_filter:
                continue
            if not api_filter and tpl.get('api_required'):
                continue

            is_dup, sim_score, orig_title = self.nlp_engine.is_duplicate_idea(tpl, existing_ideas)
            if is_dup:
                continue

            tpl_copy = dict(tpl)
            tpl_copy['duration_value'] = duration_val
            tpl_copy['duration_unit'] = duration_unit
            results.append(tpl_copy)

        for prob in self.problems:
            if domain_filter != 'All' and prob.get('domain') != domain_filter:
                continue

            prob_title = prob.get('title', '')
            prob_desc = prob.get('description', '')
            target_domain = prob.get('domain', 'Agriculture')

            cand_title = f"Offline {prob_title} Solution Platform"
            cand_dict = {"title": cand_title, "problem": prob_desc, "solution": "Standalone offline platform"}
            if any(r.get('title') == cand_title for r in results):
                continue
            is_dup, sim_score, _ = self.nlp_engine.is_duplicate_idea(cand_dict, existing_ideas)
            if is_dup:
                continue

            results.append({
                "id": f"synth_{prob.get('id', 'p')}_{datetime.now().strftime('%M%S')}",
                "domain": target_domain,
                "title": cand_title,
                "problem": prob_desc,
                "target_users": prob.get('target_users', ["Domain Users"]),
                "solution": f"A dedicated desktop/web offline software solution for {prob_title.lower()} using structured relational tables and custom analytical engines.",
                "core_features": [
                    "User Authentication & Role Management",
                    "Data Input & Validation Forms",
                    "Analytical Processing & Scoring Engine",
                    "Interactive Analytics & Progress Board",
                    "Audit Log & Printable Summary Exporter"
                ],
                "technology_stack": ["Python", "Flask", "SQLite", "Scikit-Learn", "HTML5"],
                "difficulty": difficulty_filter if difficulty_filter != 'All' else 'Intermediate',
                "duration_value": duration_val,
                "duration_unit": duration_unit,
                "estimated_duration_weeks": duration_val if duration_unit == 'Weeks' else 8,
                "team_size": team_size_filter,
                "innovation": "Runs 100% offline without cloud API dependencies, ensuring privacy and fast local processing.",
                "dataset": f"Structured {target_domain} Reference Corpus",
                "hardware": hardware_filter,
                "api_required": False,
                "complexity": "Medium"
            })

        if len(results) < 3:
            target_dom = domain_filter if domain_filter != 'All' else 'Agriculture'
            fallback_variations = [
                {
                    "title": f"Offline {target_dom} Operational Analytics & Decision Platform",
                    "problem": f"Operators in {target_dom} encounter manual delays and lack localized decision analytics.",
                    "solution": f"A standalone Python/Flask application providing structured database storage, analytical rule validation, and report export."
                },
                {
                    "title": f"{target_dom} Resource Tracking & Expiry Risk Assessor",
                    "problem": f"Stakeholders struggle to monitor resource utilization schedules in {target_dom}.",
                    "solution": f"A relational database solution with automated alert thresholds and forecasting dashboards."
                },
                {
                    "title": f"Smart {target_dom} Audit & Compliance Scanner",
                    "problem": f"Compliance checks in {target_dom} are prone to human errors and missing logs.",
                    "solution": f"An offline verification system that parses inspection files and calculates compliance scores."
                }
            ]

            for idx, fb in enumerate(fallback_variations):
                results.append({
                    "id": f"gen_fb_{idx}_{datetime.now().strftime('%M%S')}",
                    "domain": target_dom,
                    "title": fb["title"],
                    "problem": fb["problem"],
                    "target_users": ["Practitioners", "Operators"],
                    "solution": fb["solution"],
                    "core_features": [
                        "User Authentication & Roles",
                        "Data Input & Validation",
                        "Offline Processing Engine",
                        "Interactive Summary Dashboard",
                        "Audit Log & Report Export"
                    ],
                    "technology_stack": ["Python", "Flask", "SQLite", "HTML5", "CSS3"],
                    "difficulty": difficulty_filter if difficulty_filter != 'All' else 'Intermediate',
                    "duration_value": duration_val,
                    "duration_unit": duration_unit,
                    "estimated_duration_weeks": duration_val if duration_unit == 'Weeks' else 8,
                    "team_size": team_size_filter,
                    "innovation": "Runs completely offline without cloud API dependency.",
                    "dataset": f"Structured {target_dom} Dataset",
                    "hardware": hardware_filter,
                    "api_required": False,
                    "complexity": "Medium"
                })

        return results


class BlueprintGenerator:
    @staticmethod
    def generate_blueprint(project):
        if isinstance(project, dict):
            title = project.get('title', '')
            domain = project.get('domain', '')
            problem = project.get('problem', '')
            target_users = project.get('target_users', [])
            tech_stack = project.get('technology_stack', ['Python', 'Flask', 'SQLite'])
            features = project.get('core_features', [])
            hardware = project.get('hardware', 'Standard PC')
        else:
            title = getattr(project, 'title', '')
            domain = getattr(project, 'domain', '')
            problem = getattr(project, 'problem', '')
            target_users = getattr(project, 'target_users', [])
            tech_stack = project.get_tech_stack() if hasattr(project, 'get_tech_stack') else getattr(project, 'technology_stack', ['Python', 'Flask', 'SQLite'])
            features = project.get_features() if hasattr(project, 'get_features') else getattr(project, 'core_features', [])
            hardware = getattr(project, 'hardware_required', 'Standard PC')

        if isinstance(tech_stack, str):
            try:
                tech_stack = json.loads(tech_stack)
            except Exception:
                tech_stack = [tech_stack]

        if isinstance(features, str):
            try:
                features = json.loads(features)
            except Exception:
                features = [features]

        overview = f"The {title} is a dedicated offline software solution engineered to address {problem.lower() if problem else 'domain challenges'}."
        problem_statement = problem or "Real-world engineering problem statement."
        objectives = [
            f"Build a reliable offline {domain} system.",
            "Implement secure data storage using relational database tables.",
            "Provide an intuitive, responsive dashboard interface.",
            "Include automated validation and error logging."
        ]

        modules = [
            {"name": "1. Authentication & Profile Module", "description": "Handles user registration, login authentication, password security, and student profile preferences."},
            {"name": "2. Data Storage & Database Module", "description": "Manages relational schema, foreign key constraints, indexes, and queries."},
            {"name": f"3. Core {domain} Engine Module", "description": "Executes domain-specific algorithms and analytical business logic."},
            {"name": "4. User Dashboard & Presentation Module", "description": "Renders user interface screens, analytical summaries, and status cards."},
            {"name": "5. Quality Assurance & Code Analysis Module", "description": "Contains static code analysis and structural blueprint comparison checks."}
        ]

        return {
            "overview": overview,
            "problem_statement": problem_statement,
            "objectives": objectives,
            "target_users": target_users if isinstance(target_users, str) else ", ".join(target_users or []),
            "core_features": features,
            "modules": modules,
            "tech_stack": tech_stack,
            "software_requirements": ["Python 3.10+", "Flask", "SQLite", "Scikit-Learn"],
            "hardware_requirements": hardware,
            "database_requirements": "SQLite / PostgreSQL Relational Database with Foreign Key constraints",
            "architecture_overview": "Modular MVC Architecture (Flask Blueprints + SQLAlchemy ORM + Jinja2 Templates)",
            "data_flow": "User Input -> Flask Blueprint Route -> Validation -> ORM Database Query -> Service Engine -> Template View",
            "ml_methodology": "Local feature extraction and TF-IDF / Decision Tree / Rule-based classification",
            "folder_structure": "app/\n  auth/\n  core/\n  models/\n  templates/\n  static/",
            "development_phases": ["Phase 1: Setup & DB", "Phase 2: Auth & Core Logic", "Phase 3: UI & Integration", "Phase 4: Docs & Release"],
            "testing_requirements": "Static AST syntax parsing and structural code verification.",
            "deployment_requirements": "Local standalone WSGI / Gunicorn / Flask server runner.",
            "future_scope": "Support for additional local dataset formats and extended offline analytics tools."
        }


class TaskGraphGenerator:
    @staticmethod
    def calculate_total_target_hours(idea):
        val = getattr(idea, 'duration_value', None) or (idea.get('duration_value') if isinstance(idea, dict) else None)
        unit = getattr(idea, 'duration_unit', None) or (idea.get('duration_unit') if isinstance(idea, dict) else None)
        
        if not val:
            val = getattr(idea, 'estimated_duration_weeks', 8) or 8
            unit = 'Weeks'

        val = int(val)
        if unit == 'Hours':
            return max(val, 2)
        elif unit == 'Days':
            return max(val * 8, 4)
        elif unit == 'Months':
            return max(val * 160, 20)
        else: # Weeks default
            return max(val * 40, 10)

    @staticmethod
    def generate_tasks(project, blueprint, team_members=None, idea=None):
        modules = blueprint.get('modules', [])
        tasks_raw = []
        assignees = [m.member_name for m in team_members] if team_members else ["Lead Developer", "Frontend Developer", "Backend Developer"]
        
        task_id_counter = 1
        prev_task_id = None

        for idx, mod in enumerate(modules):
            mod_name = mod.get('name', f'Module {idx+1}') if isinstance(mod, dict) else str(mod)
            assignee = assignees[idx % len(assignees)]

            t1 = {
                "id": task_id_counter,
                "module_name": mod_name,
                "title": f"Design & Schema for {mod_name}",
                "description": f"Define datatypes, functions, and internal dependencies for {mod_name}.",
                "assignee_name": assignee,
                "priority": "High" if idx == 0 else "Medium",
                "required_skill": "Database" if "Database" in mod_name else "Backend",
                "status": "Pending",
                "depends_on": [prev_task_id] if prev_task_id else []
            }
            tasks_raw.append(t1)
            prev_task_id = task_id_counter
            task_id_counter += 1

            t2 = {
                "id": task_id_counter,
                "module_name": mod_name,
                "title": f"Implementation of {mod_name}",
                "description": f"Write core logic code and route handlers for {mod_name}.",
                "assignee_name": assignee,
                "priority": "High",
                "required_skill": "Full-Stack",
                "status": "Pending",
                "depends_on": [t1["id"]]
            }
            tasks_raw.append(t2)
            prev_task_id = task_id_counter
            task_id_counter += 1

        # Calculate exact total target hours from project/idea duration
        total_hours = TaskGraphGenerator.calculate_total_target_hours(idea) if idea else 40
        num_tasks = max(len(tasks_raw), 1)

        base_hours = total_hours // num_tasks
        remainder = total_hours % num_tasks

        for i, t in enumerate(tasks_raw):
            # Assign baseline hours + remainder distribution so SUM == total_hours
            assigned_h = base_hours + (1 if i < remainder else 0)
            t["estimated_hours"] = max(assigned_h, 1)

        return tasks_raw


class RoadmapGenerator:
    @staticmethod
    def generate_roadmap(duration_weeks, tasks):
        total_weeks = duration_weeks or 8
        weeks_data = []

        tasks_per_week = max(1, len(tasks) // total_weeks)

        for w in range(1, total_weeks + 1):
            start_idx = (w - 1) * tasks_per_week
            end_idx = start_idx + tasks_per_week if w < total_weeks else len(tasks)
            week_tasks = tasks[start_idx:end_idx]

            milestone_title = f"Week {w} Milestone: Complete Phase {w}"
            deliverables = [t["title"] for t in week_tasks] if week_tasks else [f"System Refinement Phase {w}"]

            weeks_data.append({
                "week": w,
                "title": milestone_title,
                "deliverables": deliverables,
                "tasks": week_tasks
            })

        return {
            "total_weeks": total_weeks,
            "weeks": weeks_data
        }


class ProjectMentorEngine:
    @staticmethod
    def answer_query(query, project, blueprint, analysis, tasks):
        q = query.lower().strip()
        p_title = getattr(project, 'title', 'your project') if project else 'your project'
        p_domain = getattr(project, 'domain', 'engineering') if project else 'engineering'

        greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening', 'who are you', 'help', 'hi!', 'hello!', 'hey!']
        if q in greetings or any(q == g or q.startswith(g + ' ') or q.endswith(' ' + g) for g in ['hi', 'hello', 'hey', 'greetings']):
            p_status = getattr(project, 'status', 'planning') if project else 'planning'
            p_pct = getattr(project, 'progress_percentage', 0) if project else 0

            return (
                f"Hello! 👋 I am your dedicated Senior Project Mentor for **{p_title}**.\n\n"
                f"I have reviewed your {p_domain} project setup ({p_status} phase, {p_pct}% progress).\n\n"
                f"**Here's how I can help you today:**\n"
                f"• **Recommended Next Steps** (Ask: *'What should I implement next?'*)\n"
                f"• **Project Overview & Blueprint** (Ask: *'Explain my project blueprint'*) \n"
                f"• **Task Breakdown** (Ask: *'Show my pending tasks'*)\n"
                f"• **Code Analysis & Inspection** (Ask: *'Check my codebase status'*)\n\n"
                f"What would you like to focus on right now?"
            )

        if any(k in q for k in ['project', 'overview', 'about', 'problem', 'solution', 'tell me']):
            b_overview = getattr(blueprint, 'overview', 'Detailed offline software solution.') if blueprint else 'Planned software system.'
            b_problem = getattr(blueprint, 'problem_statement', 'Engineering domain problem.') if blueprint else 'Domain challenge.'
            
            return (
                f"**Project Context — {p_title}**\n\n"
                f"• **Domain:** {p_domain}\n"
                f"• **Problem Statement:** {b_problem}\n"
                f"• **System Overview:** {b_overview}\n\n"
                f"You can review your full architecture and folder structure under the **Project Blueprint** tab."
            )

        if any(k in q for k in ['start', 'next', 'work on', 'what should i do', 'task', 'pending', 'progress', 'status']):
            if analysis and getattr(analysis, 'development_guidance_json', None):
                try:
                    guidance = json.loads(analysis.development_guidance_json or '{}')
                    if guidance.get('recommended_next_step'):
                        return (
                            f"Based on our AST code analysis of your project:\n\n"
                            f"📌 **Recommended Next Step:** {guidance.get('recommended_next_step')}\n\n"
                            f"📊 **Current Implementation Progress:** {guidance.get('progress_percentage', 0)}%\n"
                            f"• Auth Module: {'✅ Detected' if guidance.get('has_auth') else '❌ Missing'}\n"
                            f"• Database Models: {'✅ Detected' if guidance.get('has_database') else '❌ Missing'}"
                        )
                except Exception:
                    pass

            pending_tasks = [t for t in tasks if getattr(t, 'status', 'Pending') != 'Completed'] if tasks else []
            if pending_tasks:
                next_t = pending_tasks[0]
                return (
                    f"According to your team task distribution graph:\n\n"
                    f"📋 **Next Priority Task:** #{next_t.id} — {next_t.title}\n"
                    f"• **Module:** {next_t.module_name}\n"
                    f"• **Assigned To:** {next_t.assignee_name or 'Team'}\n"
                    f"• **Priority:** {next_t.priority} ({next_t.estimated_hours} hrs estimated)\n"
                    f"• **Description:** {next_t.description}"
                )
            
            return f"Great job! All planned tasks for **{p_title}** are currently marked completed. Run the **Project Analyzer** to verify your codebase against the blueprint!"

        if any(k in q for k in ['blueprint', 'module', 'architecture', 'stack', 'tech', 'technology', 'database', 'sqlite']):
            if blueprint:
                b_overview = getattr(blueprint, 'overview', '')
                b_arch = getattr(blueprint, 'architecture_overview', '')
                b_stack = getattr(blueprint, 'tech_stack_json', 'Python, Flask, SQLite')
                b_db = getattr(blueprint, 'database_requirements', 'Relational Database')
                return (
                    f"**Architecture & Tech Stack Breakdown for {p_title}:**\n\n"
                    f"• **Tech Stack:** {b_stack}\n"
                    f"• **Database Specs:** {b_db}\n"
                    f"• **Architecture:** {b_arch}\n"
                    f"• **System Overview:** {b_overview}"
                )

        return (
            f"I am your dedicated mentor for **{p_title}**.\n\n"
            f"Here are key areas I can assist you with right now:\n"
            f"1. *'What should I implement next?'*\n"
            f"2. *'Explain my project blueprint and database requirements'*\n"
            f"3. *'What is the status of my team's tasks?'*\n"
            f"4. *'How do I document this project?'*"
        )


class DocPresentationResumeGenerator:
    @staticmethod
    def generate_documentation(project, blueprint, analysis):
        detected_files = json.loads(analysis.files_detected or '[]') if analysis and getattr(analysis, 'files_detected', None) else []
        detected_routes = json.loads(analysis.routes_detected or '[]') if analysis and getattr(analysis, 'routes_detected', None) else []
        detected_models = json.loads(analysis.models_detected or '[]') if analysis and getattr(analysis, 'models_detected', None) else []

        guidance = json.loads(analysis.development_guidance_json or '{}') if analysis and getattr(analysis, 'development_guidance_json', None) else {}
        has_auth = guidance.get('has_auth', False)

        auth_str = "Authentication module detected." if has_auth else "Authentication was not detected in the analyzed project."
        db_str = f"Database models detected ({len(detected_models)} models: {', '.join(detected_models)})." if len(detected_models) > 0 else "Database models were not detected in the analyzed project."

        title = getattr(project, 'title', 'Project')
        domain = getattr(project, 'domain', 'General')
        problem = getattr(project, 'problem', 'Engineering Problem')
        status = getattr(project, 'status', 'Development')

        folder_struct = getattr(blueprint, 'folder_structure', 'app/\n  models/\n  templates/\n  static/') if blueprint else 'app/\n  models/\n  templates/\n  static/'
        if detected_files:
            file_tree_str = "\n".join([f"├── {f}" for f in detected_files])
        else:
            file_tree_str = folder_struct

        abstract = f"This document presents the official Software Requirements Specification and Implementation Report for {title}. The system operates in the {domain} domain, solving: {problem}"

        srs = f"""# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## 1. System Overview
System Name: {title}
Domain Category: {domain}
Project Status: {status}

## 2. Verified Implementation Status
- {auth_str}
- {db_str}

## 3. Detected Application Routes
{chr(10).join(['- ' + r for r in detected_routes]) if detected_routes else 'No Flask routes detected.'}

## 4. Verified Project Structure & Code Files
Total Files Analyzed: {len(detected_files)}
```
{file_tree_str}
```
"""

        readme = f"""# {title}

## Project Overview
{problem}

## Technologies Used
{getattr(blueprint, 'tech_stack_json', 'Python, Flask, SQLite') if blueprint else 'Python, Flask, SQLite'}

## Verified Project Folder Structure
```
{file_tree_str}
```

## Quick Start
1. Install Python 3.10+
2. Install dependencies: `pip install -r requirements.txt`
3. Run application: `python run.py`
"""

        full_report = f"# FULL PROJECT IMPLEMENTATION REPORT\n\n## Abstract\n{abstract}\n\n{srs}\n\n## README\n{readme}\n\n## Conclusion\nProjectPartner structural verification completed successfully."

        return {
            "abstract": abstract,
            "srs_content": srs,
            "readme_content": readme,
            "full_report_content": full_report
        }

    @staticmethod
    def generate_pdf_documentation(user, project, blueprint, doc):
        from io import BytesIO
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        buffer = BytesIO()
        doc_pdf = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#143965"),
            spaceAfter=6,
            fontName="Helvetica-Bold"
        )
        
        subtitle_style = ParagraphStyle(
            'DocSubTitle',
            parent=styles['Normal'],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#17899b"),
            spaceAfter=14,
            fontName="Helvetica-Bold"
        )
        
        h2_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#143965"),
            spaceBefore=12,
            spaceAfter=6,
            fontName="Helvetica-Bold"
        )
        
        body_style = ParagraphStyle(
            'BodyTextCustom',
            parent=styles['BodyText'],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=6
        )

        story = []
        
        # Header Banner
        story.append(Paragraph("PROJECTPARTNER STUDENT PROJECT SPECIFICATION", title_style))
        story.append(Paragraph("Official Engineering Documentation — User Metadata & Project Context Report", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#143965"), spaceAfter=12))
        
        # Section 1: User Information Details
        story.append(Paragraph("1. Student / User Details", h2_style))
        u_name = getattr(user, 'name', 'Student Engineer') if user else 'Student Engineer'
        u_email = getattr(user, 'email', 'N/A') if user else 'N/A'
        u_college = getattr(user, 'college', 'Engineering College') if user else 'Engineering College'
        u_branch = getattr(user, 'branch', 'Computer Science / Engineering') if user else 'Computer Science / Engineering'
        u_year = getattr(user, 'year', '3rd Year') if user else '3rd Year'

        user_data = [
            [Paragraph("<b>Student Name:</b>", body_style), Paragraph(u_name, body_style), Paragraph("<b>Email Address:</b>", body_style), Paragraph(u_email, body_style)],
            [Paragraph("<b>College / Univ:</b>", body_style), Paragraph(u_college or 'Engineering Univ', body_style), Paragraph("<b>Branch / Dept:</b>", body_style), Paragraph(u_branch or 'Computer Science', body_style)],
            [Paragraph("<b>Academic Year:</b>", body_style), Paragraph(u_year or '3rd Year', body_style), Paragraph("<b>Assigned Role:</b>", body_style), Paragraph("Lead Project Author", body_style)],
        ]
        t1 = Table(user_data, colWidths=[110, 160, 110, 160])
        t1.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#e2e8f0")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t1)
        story.append(Spacer(1, 10))

        # Section 2: Project Metadata & Problem Statement
        story.append(Paragraph("2. Project Context & Problem Statement", h2_style))
        p_title = getattr(project, 'title', 'N/A') if project else 'N/A'
        p_domain = getattr(project, 'domain', 'N/A') if project else 'N/A'
        p_status = getattr(project, 'status', 'Development') if project else 'Development'
        p_prog = getattr(project, 'progress_percentage', 0) if project else 0
        p_problem = getattr(blueprint, 'problem_statement', None) if blueprint else None
        if not p_problem and project:
            p_problem = getattr(project, 'problem', 'Real-world engineering challenge requiring modular offline software solution.')
        if not p_problem:
            p_problem = 'Real-world engineering challenge requiring modular offline software solution.'

        proj_data = [
            [Paragraph("<b>Project Title:</b>", body_style), Paragraph(p_title, body_style), Paragraph("<b>Domain Category:</b>", body_style), Paragraph(p_domain, body_style)],
            [Paragraph("<b>Lifecycle Phase:</b>", body_style), Paragraph(p_status, body_style), Paragraph("<b>Progress Status:</b>", body_style), Paragraph(f"{p_prog}% Completed", body_style)],
        ]
        t2 = Table(proj_data, colWidths=[110, 160, 110, 160])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#e2e8f0")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t2)
        story.append(Spacer(1, 6))

        story.append(Paragraph("<b>Problem Statement:</b>", body_style))
        story.append(Paragraph(p_problem, body_style))
        story.append(Spacer(1, 10))

        # Section 3: Abstract of the Project
        story.append(Paragraph("3. Project Abstract", h2_style))
        abstract_text = getattr(doc, 'abstract', None) if doc else None
        if not abstract_text:
            abstract_text = f"This official documentation presents the Software Requirements Specification and structural details for {p_title}. Operating in the {p_domain} domain, the solution provides structured database processing and local analytics."
        story.append(Paragraph(abstract_text, body_style))
        story.append(Spacer(1, 10))

        # Section 4: Software Requirements & Technical Stack
        story.append(Paragraph("4. Software Requirements & Technical Specification", h2_style))
        tech_stack = getattr(blueprint, 'tech_stack_json', 'Python, Flask, SQLite') if blueprint else 'Python, Flask, SQLite'
        arch_overview = getattr(blueprint, 'architecture_overview', 'Modular MVC Architecture (Flask Blueprints + SQLAlchemy ORM)') if blueprint else 'Modular MVC Architecture'
        
        spec_data = [
            [Paragraph("<b>Technology Stack:</b>", body_style), Paragraph(str(tech_stack), body_style)],
            [Paragraph("<b>Architecture:</b>", body_style), Paragraph(str(arch_overview), body_style)],
        ]
        t3 = Table(spec_data, colWidths=[130, 410])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#e2e8f0")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t3)

        doc_pdf.build(story)
        buffer.seek(0)
        return buffer.getvalue()
