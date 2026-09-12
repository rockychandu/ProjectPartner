from backend.algorithms.generators import ProjectMentorEngine

def test_mentor_project_specific_query():
    proj = type('obj', (object,), {'title': 'Agri Vision', 'domain': 'Agriculture', 'status': 'Development', 'progress_percentage': 50})
    blueprint = type('obj', (object,), {
        'overview': 'Agri Vision Leaf System',
        'architecture_overview': 'Flask MVC',
        'tech_stack_json': 'Python, Flask'
    })
    analysis = type('obj', (object,), {
        'development_guidance_json': '{"recommended_next_step": "Implement unit tests", "progress_percentage": 50}'
    })

    # Test greeting query ("hi")
    greeting_ans = ProjectMentorEngine.answer_query("hi", proj, blueprint, analysis, [])
    assert "Hello!" in greeting_ans
    assert "Agri Vision" in greeting_ans

    # Test next step query
    ans = ProjectMentorEngine.answer_query("what should i implement next?", proj, blueprint, analysis, [])
    assert "Implement unit tests" in ans

    # Test out of domain query
    ans_unknown = ProjectMentorEngine.answer_query("what is quantum computing?", proj, blueprint, analysis, [])
    assert "dedicated mentor" in ans_unknown.lower()
