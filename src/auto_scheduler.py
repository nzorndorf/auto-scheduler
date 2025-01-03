from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import random

def simple_round_robin_auto_schedule(data: Dict) -> List[Tuple[Dict, Dict]]:
    """
    Simple round robin job scheduling algorithm that assigns jobs to resources in rotation,
    without considering skill matching.
    
    Parameters:
    - data: Input data containing jobs, resources and date range
    
    Returns:
    - List of (event, event_assignment) tuples
    """
    # Validate date range
    start_date = datetime.strptime(data["date_range"]["start_date"], "%Y-%m-%d")
    end_date = datetime.strptime(data["date_range"]["end_date"], "%Y-%m-%d")
    
    if end_date < start_date:
        raise ValueError("End date cannot be before start date")

    job_ids = data["job_ids"]
    resources = data["resources"]

    # Initialize resource availability
    resource_availability = {res["id"]: start_date for res in resources}
    
    # Initialize round robin pointer
    current_resource_index = 0
    
    # Job schedule output
    job_schedule = []

    # Process jobs one by one
    for job_id in job_ids:
        # Get next available resource in round robin fashion
        resource = resources[current_resource_index]
        resource_id = resource["id"]
        
        # Get assignment date
        job_date = resource_availability[resource_id]
        
        # Only schedule if within date range
        if job_date <= end_date:
            # Create event and event_assignment
            event = {
                "name": f"Job {job_id}",
                "job_id": job_id,
                "start_date": job_date.strftime("%Y-%m-%d"),
                "end_date": job_date.strftime("%Y-%m-%d"),
                "start_time": None,
                "end_time": None
            }
            
            event_assignment = {
                "id": None,
                "event_id": None,
                "resource_id": resource_id,
                "key": None
            }
            
            # Add to schedule
            job_schedule.append((event, event_assignment))
            
            # Update resource availability
            resource_availability[resource_id] += timedelta(days=1)
        
        # Move to next resource
        current_resource_index = (current_resource_index + 1) % len(resources)

    return job_schedule

def round_robin_with_skills_autoschedule(data: Dict) -> List[Tuple[Dict, Dict]]:
    job_ids = data["job_ids"]
    resources = data["resources"]
    jobs = data["jobs"]
    start_date = datetime.strptime(data["date_range"]["start_date"], "%Y-%m-%d")
    end_date = datetime.strptime(data["date_range"]["end_date"], "%Y-%m-%d")

    # Initialize availability for each resource
    resource_availability = {res["id"]: start_date for res in resources}

    # Keep track of where we are in the round-robin cycle for each skill group
    round_robin_pointers = {}

    # Job schedule output
    job_schedule = []

    # Helper function to filter resources based on job skills
    def get_eligible_resources(required_skills):
        return [res for res in resources if set(required_skills).issubset(res["skills"])]

    # Process jobs one by one
    for job in jobs:
        job_id = job["id"]
        required_skills = job["required_skills"]

        # Find all eligible resources
        eligible_resources = get_eligible_resources(required_skills)
        if not eligible_resources:
            print(f"Warning: No resources available for job {job_id}.")
            continue

        # Initialize round-robin pointer for this skill group if not already initialized
        skill_key = "_".join(sorted(required_skills))  # Unique key for this skill group
        if skill_key not in round_robin_pointers:
            round_robin_pointers[skill_key] = 0

        # Find the next eligible resource in round-robin order
        num_resources = len(eligible_resources)
        start_index = round_robin_pointers[skill_key]
        chosen_resource = None
        for i in range(num_resources):
            index = (start_index + i) % num_resources  # Cycle through resources
            resource = eligible_resources[index]
            if resource_availability[resource["id"]] <= end_date:
                chosen_resource = resource
                round_robin_pointers[skill_key] = (index + 1) % num_resources  # Update pointer
                break

        if not chosen_resource:
            print(f"Warning: No available resources for job {job_id} within the date range.")
            continue

        # Assign the job to the chosen resource
        resource_id = chosen_resource["id"]
        job_date = resource_availability[resource_id]

        # Create "event" and "event_assignment"
        event = {
            "name": f"Job {job_id}",
            "job_id": job_id,
            "start_date": job_date.strftime("%Y-%m-%d"),
            "end_date": job_date.strftime("%Y-%m-%d"),
            "start_time": None,
            "end_time": None
        }
        event_assignment = {
            "id": None,
            "event_id": None,
            "resource_id": resource_id,
            "key": None
        }

        # Append to the schedule
        job_schedule.append((event, event_assignment))

        # Update resource availability to the next day
        resource_availability[resource_id] += timedelta(days=1)

    return job_schedule