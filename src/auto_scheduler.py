from typing import Dict, List, Tuple
from datetime import datetime, timedelta

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