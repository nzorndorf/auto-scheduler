import pytest
from datetime import datetime, timedelta
from src.auto_scheduler import round_robin_with_skills_autoschedule

@pytest.fixture
def basic_input_data():
    return {
        "date_range": {
            "start_date": "2024-01-01",
            "end_date": "2024-01-05"  # 5 days
        },
        "job_ids": [f"job{i}" for i in range(1, 11)],  # 10 jobs
        "jobs": [
            {"id": "job1", "required_skills": ["skill1"]},
            {"id": "job2", "required_skills": ["skill1", "skill2"]},
            {"id": "job3", "required_skills": ["skill2"]},
            {"id": "job4", "required_skills": ["skill1"]},
            {"id": "job5", "required_skills": ["skill2"]},
            {"id": "job6", "required_skills": ["skill1", "skill2"]},
            {"id": "job7", "required_skills": ["skill1"]},
            {"id": "job8", "required_skills": ["skill2"]},
            {"id": "job9", "required_skills": ["skill1"]},
            {"id": "job10", "required_skills": ["skill2"]}
        ],
        "resources": [
            {"id": "res1", "skills": ["skill1", "skill2"]},
            {"id": "res2", "skills": ["skill1", "skill2"]}
        ]
    }

def test_basic_scheduling(basic_input_data):
    result = round_robin_with_skills_autoschedule(basic_input_data)
    
    # Check if all jobs are scheduled
    assert len(result) == 10  # Updated to expect 10 jobs
    
    # Check if each result has correct structure
    for event, assignment in result:
        assert isinstance(event, dict)
        assert isinstance(assignment, dict)
        assert "job_id" in event
        assert "resource_id" in assignment

def test_resource_distribution(basic_input_data):
    """Test that jobs are distributed fairly between resources"""
    result = round_robin_with_skills_autoschedule(basic_input_data)
    
    # Count assignments per resource
    resource_counts = {}
    for _, assignment in result:
        resource_id = assignment["resource_id"]
        resource_counts[resource_id] = resource_counts.get(resource_id, 0) + 1
    
    # With 10 jobs and 2 resources, each should have 5 jobs ± 1
    for count in resource_counts.values():
        assert abs(count - 5) <= 1

def test_date_range_limits(basic_input_data):
    """Test that all jobs are scheduled within the date range"""
    result = round_robin_with_skills_autoschedule(basic_input_data)
    
    start_date = datetime.strptime("2024-01-01", "%Y-%m-%d")
    end_date = datetime.strptime("2024-01-05", "%Y-%m-%d")
    
    for event, _ in result:
        job_date = datetime.strptime(event["start_date"], "%Y-%m-%d")
        assert start_date <= job_date <= end_date, \
            f"Job scheduled on {job_date} is outside range {start_date} to {end_date}"