import pytest
from datetime import datetime
from src.auto_scheduler import simple_round_robin_auto_schedule

def test_simple_round_robin_auto_schedule():
    # Test input data
    test_data = {
        "job_ids": [f"job_{i}" for i in range(1, 11)],  # 10 jobs
        "resource_ids": ["res_1", "res_2"],
        "date_range": {
            "start_date": "2024-06-01",
            "end_date": "2024-06-05"  # 5 days
        },
        "resources": [
            {"id": "res_1", "skills": ["electric"]},
            {"id": "res_2", "skills": ["repair"]}
        ],
        "jobs": [
            {"id": "job_1", "required_skills": ["electric"]},
            {"id": "job_2", "required_skills": ["repair"]},
            {"id": "job_3", "required_skills": ["electric"]},
            {"id": "job_4", "required_skills": ["repair"]},
            {"id": "job_5", "required_skills": ["electric"]},
            {"id": "job_6", "required_skills": ["repair"]},
            {"id": "job_7", "required_skills": ["electric"]},
            {"id": "job_8", "required_skills": ["repair"]},
            {"id": "job_9", "required_skills": ["electric"]},
            {"id": "job_10", "required_skills": ["repair"]}
        ]
    }

    # Get schedule
    schedule = simple_round_robin_auto_schedule(test_data)

    # Test 1: Check all jobs are assigned
    assert len(schedule) == 10, "Not all jobs were assigned"

    # Test 2: Check round robin distribution
    resource_assignments = {}
    for event, assignment in schedule:
        res_id = assignment["resource_id"]
        resource_assignments[res_id] = resource_assignments.get(res_id, 0) + 1
    
    # Each resource should have equal or almost equal number of jobs
    assignment_counts = list(resource_assignments.values())
    assert max(assignment_counts) - min(assignment_counts) <= 1, "Jobs not evenly distributed"

    # Test 3: Check date assignments are sequential and within range
    start_date = datetime.strptime(test_data["date_range"]["start_date"], "%Y-%m-%d")
    end_date = datetime.strptime(test_data["date_range"]["end_date"], "%Y-%m-%d")
    
    for event, _ in schedule:
        job_date = datetime.strptime(event["start_date"], "%Y-%m-%d")
        assert start_date <= job_date <= end_date, "Job scheduled outside date range"

def test_simple_round_robin_date_overflow():
    # Test data with more jobs than available days
    test_data = {
        "job_ids": ["job_1", "job_2", "job_3", "job_4"],
        "resource_ids": ["res_1"],
        "date_range": {
            "start_date": "2024-06-01",
            "end_date": "2024-06-02"  # Only 2 days
        },
        "resources": [
            {"id": "res_1", "skills": ["electric"]}
        ],
        "jobs": [
            {"id": "job_1", "required_skills": ["electric"]},
            {"id": "job_2", "required_skills": ["electric"]},
            {"id": "job_3", "required_skills": ["electric"]},
            {"id": "job_4", "required_skills": ["electric"]}
        ]
    }

    schedule = simple_round_robin_auto_schedule(test_data)
    
    # Should only schedule jobs that fit within date range
    assert len(schedule) == 2, "Should only schedule jobs that fit in date range"

def test_simple_round_robin_empty_input():
    # Test with empty job list
    test_data = {
        "job_ids": [],
        "resource_ids": ["res_1"],
        "date_range": {
            "start_date": "2024-06-01",
            "end_date": "2024-06-02"
        },
        "resources": [
            {"id": "res_1", "skills": ["electric"]}
        ],
        "jobs": []
    }

    schedule = simple_round_robin_auto_schedule(test_data)
    assert len(schedule) == 0, "Empty job list should produce empty schedule"

def test_simple_round_robin_date_validation():
    # Test with invalid date range
    test_data = {
        "job_ids": ["job_1"],
        "resource_ids": ["res_1"],
        "date_range": {
            "start_date": "2024-06-02",
            "end_date": "2024-06-01"  # End date before start date
        },
        "resources": [
            {"id": "res_1", "skills": ["electric"]}
        ],
        "jobs": [
            {"id": "job_1", "required_skills": ["electric"]}
        ]
    }

    with pytest.raises(ValueError):
        simple_round_robin_auto_schedule(test_data)

def test_schedule_format():
    # Test the format of schedule output
    test_data = {
        "job_ids": ["job_1"],
        "resource_ids": ["res_1"],
        "date_range": {
            "start_date": "2024-06-01",
            "end_date": "2024-06-02"
        },
        "resources": [
            {"id": "res_1", "skills": ["electric"]}
        ],
        "jobs": [
            {"id": "job_1", "required_skills": ["electric"]}
        ]
    }

    schedule = simple_round_robin_auto_schedule(test_data)
    
    assert len(schedule) == 1
    event, assignment = schedule[0]
    
    # Check event format
    assert isinstance(event, dict)
    assert all(key in event for key in ["name", "job_id", "start_date", "end_date", "start_time", "end_time"])
    
    # Check assignment format
    assert isinstance(assignment, dict)
    assert all(key in assignment for key in ["id", "event_id", "resource_id", "key"])