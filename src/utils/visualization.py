import matplotlib.pyplot as plt
import pandas as pd
import textwrap
from datetime import datetime
from typing import List, Dict, Tuple

def visualize_job_assignments(job_schedule: List[Tuple[Dict, Dict]], 
                            resources: List[Dict], 
                            date_range: Dict, 
                            jobs: List[Dict], 
                            title: str) -> None:
    """
    Create a visualization of job assignments with enhanced labels.
    
    Parameters:
    - job_schedule: List of (event, event_assignment) tuples
    - resources: List of resource dictionaries
    - date_range: Dictionary with start_date and end_date
    - jobs: List of job dictionaries
    - title: Title for the visualization
    """
    start_date = datetime.strptime(date_range["start_date"], "%Y-%m-%d")
    end_date = datetime.strptime(date_range["end_date"], "%Y-%m-%d")
    dates = pd.date_range(start=start_date, end=end_date)

    # Initialize empty table with resources (rows) and dates (columns)
    table_data = pd.DataFrame("", index=[res["id"] for res in resources], columns=dates.date)
    resource_skills = {res["id"]: ", ".join(res["skills"]) for res in resources}
    job_skills = {job["id"]: ", ".join(job["required_skills"]) for job in jobs}

    # Populate the table
    for event, assignment in job_schedule:
        resource_id = assignment["resource_id"]
        job_date = datetime.strptime(event["start_date"], "%Y-%m-%d").date()
        job_id = event["job_id"]
        if job_date in table_data.columns:
            wrapped_skills = textwrap.fill(f"{job_id} ({job_skills[job_id]})", width=10)
            table_data.at[resource_id, job_date] = wrapped_skills

    # Plot setup
    fig, ax = plt.subplots(figsize=(len(dates)+4, len(resources)+4))
    ax.axis("off")
    ax.set_title(f"Job Assignments with Resource and Job Skills - {title}", fontsize=14, weight="bold")

    # Color formatting
    cell_colors = []
    for res_id in table_data.index:
        row_colors = []
        for date in table_data.columns:
            row_colors.append("beige" if table_data.at[res_id, date] == "" else "lightblue")
        cell_colors.append(row_colors)

    # Row labels with resource skills
    row_labels = [f"{res_id}\n({textwrap.fill(resource_skills[res_id], width=10)})" for res_id in table_data.index]

    # Create and format table
    table_data.columns = pd.to_datetime(table_data.columns)
    table = ax.table(
        cellText=table_data.values,
        rowLabels=row_labels,
        colLabels=[date.strftime("%Y-%m-%d") for date in table_data.columns],
        cellColours=cell_colors,
        loc="center"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.auto_set_column_width(col=list(range(len(table_data.columns))))

    # Adjust cell sizes
    for (i, j), cell in table.get_celld().items():
        cell.set_height(0.08)
        cell.set_width(0.1)

    plt.show()