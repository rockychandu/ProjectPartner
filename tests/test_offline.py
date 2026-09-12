import pytest
import socket
from backend.algorithms.generators import (
    CombinatorialProjectGenerator,
    BlueprintGenerator,
    TaskGraphGenerator,
    RoadmapGenerator,
    ProjectMentorEngine,
    DocPresentationResumeGenerator
)
from backend.algorithms.nlp_engine import RecommendationEngine, LocalNLPEngine
from backend.algorithms.ast_analyzer import BlueprintComparator, ProjectDirectoryAnalyzer
from backend.models.models import StudentProfile, ProjectIdea

def test_tc_api_001_offline_execution(monkeypatch):
    """
    TC-API-001: Verifies that all core platform operations execute completely offline
    with ZERO external HTTP or socket API requests.
    """
    def block_network(*args, **kwargs):
        raise RuntimeError("External network connection attempted! Violation of offline rule.")

    monkeypatch.setattr(socket, 'socket', block_network)

    # 1. Project Generation
    gen = CombinatorialProjectGenerator()
    candidates = gen.generate_candidates({'domain': 'Agriculture', 'api_allowed': False})
    assert len(candidates) > 0

    # 2. Recommendation Scoring
    prof = StudentProfile(skills='["Python"]', technologies='["Flask"]')
    ranked = RecommendationEngine.rank_projects(prof, [ProjectIdea(title="Agri Proj", core_features='[]', technology_stack='["Flask"]')])
    assert len(ranked) > 0

    # 3. Blueprint Generation
    bp = BlueprintGenerator.generate_blueprint({'title': 'Offline Proj', 'problem': 'Test', 'domain': 'Edu'})
    assert bp['overview'] is not None

    # 4. Task Graph Distribution
    tasks = TaskGraphGenerator.generate_tasks({'title': 'P'}, bp)
    assert len(tasks) > 0

    # 5. Roadmap Generation
    rm = RoadmapGenerator.generate_roadmap(4, tasks)
    assert rm['total_weeks'] == 4

    # 6. Project Mentor
    proj = type('obj', (object,), {'title': 'Offline P', 'domain': 'Edu'})
    ans = ProjectMentorEngine.answer_query("what should i do next?", proj, None, None, [])
    assert ans is not None

    # 7. Documentation & PDF Generation
    docs = DocPresentationResumeGenerator.generate_documentation(proj, None, None)
    pdf_bytes = DocPresentationResumeGenerator.generate_pdf_documentation(None, proj, None, None)
    
    assert docs['abstract'] is not None
    assert len(pdf_bytes) > 0

    # Zero External API Calls verified!
