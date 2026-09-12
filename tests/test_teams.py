from backend.algorithms.generators import TaskGraphGenerator, RoadmapGenerator

def test_task_graph_dependencies():
    project_dict = {"title": "Test Proj", "domain": "Education"}
    blueprint = {
        "modules": [
            {"name": "Auth Module"},
            {"name": "Database Module"}
        ]
    }
    tasks = TaskGraphGenerator.generate_tasks(project_dict, blueprint)
    assert len(tasks) == 4
    # Check directed dependency
    t2 = tasks[1]
    assert len(t2["depends_on"]) > 0

def test_roadmap_milestone_generator():
    tasks = [{"title": "Task 1"}, {"title": "Task 2"}, {"title": "Task 3"}, {"title": "Task 4"}]
    rm = RoadmapGenerator.generate_roadmap(4, tasks)
    assert rm["total_weeks"] == 4
    assert len(rm["weeks"]) == 4
