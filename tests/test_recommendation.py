from backend.models.models import StudentProfile, ProjectIdea
from backend.algorithms.nlp_engine import RecommendationEngine

def test_recommendation_ranking_engine():
    profile = StudentProfile(
        programming_languages='["Python"]',
        technologies='["Flask", "OpenCV"]',
        skills='["Computer Vision", "Backend"]',
        preferred_difficulty='Intermediate',
        available_time_hours_per_week=10
    )

    p1 = ProjectIdea(
        title="Agri Vision System",
        domain="Agriculture",
        problem="Disease in crops",
        core_features='["CV", "Flask"]',
        technology_stack='["Python", "OpenCV", "Flask"]',
        difficulty="Intermediate",
        estimated_duration_weeks=8,
        team_size=3,
        api_required=False
    )

    p2 = ProjectIdea(
        title="Web E-Commerce Store",
        domain="E-Commerce",
        problem="Inventory management",
        core_features='["Cart"]',
        technology_stack='["Node.js", "Express"]',
        difficulty="Beginner",
        estimated_duration_weeks=4,
        team_size=2,
        api_required=False
    )

    ranked = RecommendationEngine.rank_projects(profile, [p1, p2])
    assert len(ranked) == 2
    # p1 should match Python, OpenCV, Flask much higher than p2
    assert ranked[0]['project'].title == "Agri Vision System"
    assert ranked[0]['overall_match'] > ranked[1]['overall_match']
