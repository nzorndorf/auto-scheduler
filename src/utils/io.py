import json
import random
from typing import Dict, List, Tuple

def export_job_schedule_to_json(job_schedule: List[Tuple[Dict, Dict]], filename: str) -> None:
    """
    Export the job schedule to a JSON file.
    
    Parameters:
    - job_schedule: The list containing job events and assignments
    - filename: The name of the output JSON file
    """
    export_data = []
    for event, assignment in job_schedule:
        export_data.append({
            "event": {
                "name": event["name"],
                "job_id": event["job_id"],
                "start_date": event["start_date"],
                "end_date": event["end_date"],
                "start_time": event.get("start_time"),
                "end_time": event.get("end_time"),
            },
            "event_assignment": {
                "id": assignment.get("id"),
                "event_id": assignment.get("event_id"),
                "resource_id": assignment["resource_id"],
                "key": assignment.get("key"),
            }
        })
    
    with open(filename, "w") as json_file:
        json.dump(export_data, json_file, indent=4)
    
    print(f"Job schedule exported successfully to {filename}")

def generate_random_name() -> str:
    """
    Generate a random job name.
    
    Returns:
    - A randomly selected job name
    """
    names = ["Inspection", "Repair", "Maintenance", "Installation", "Survey", "Configuration"]
    return random.choice(names)