from backend.algorithms.generators import CombinatorialProjectGenerator
from backend.algorithms.nlp_engine import LocalNLPEngine

def test_combinatorial_project_generator():
    generator = CombinatorialProjectGenerator()
    filters = {
        'domain': 'Agriculture',
        'technology': 'All',
        'difficulty': 'Intermediate',
        'duration': 8,
        'team_size': 3,
        'api_allowed': False,
        'hardware_required': 'Not Required'
    }
    
    candidates = generator.generate_candidates(filters)
    assert len(candidates) > 0
    cand = candidates[0]
    assert cand['domain'] == 'Agriculture'
    assert cand['api_required'] is False

def test_duplicate_idea_detection():
    nlp = LocalNLPEngine()
    existing = [
        {"title": "Offline Leaf Pest & Disease Identification System", "problem": "Crop disease in leaves", "solution": "Computer vision analysis"}
    ]
    candidate = {
        "title": "Offline Leaf Pest & Disease Identification System",
        "problem": "Crop disease in leaves",
        "solution": "Computer vision analysis"
    }

    is_dup, score, orig = nlp.is_duplicate_idea(candidate, existing)
    assert is_dup is True
    assert score > 0.75
