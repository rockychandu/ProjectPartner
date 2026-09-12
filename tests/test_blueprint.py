from backend.algorithms.generators import BlueprintGenerator

def test_dynamic_blueprint_generation():
    project_dict = {
        "title": "Offline Leaf Pest Identification",
        "domain": "Agriculture",
        "problem": "Crop disease diagnosis",
        "target_users": ["Farmers"],
        "core_features": ["Upload", "Prediction"],
        "technology_stack": ["Python", "Flask", "SQLite"]
    }

    bp = BlueprintGenerator.generate_blueprint(project_dict)
    assert "Offline Leaf Pest Identification" in bp["overview"]
    assert len(bp["modules"]) > 0
    assert len(bp["objectives"]) > 0
    assert "SQLite" in bp["database_requirements"]
