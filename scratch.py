from ortools.sat.python import cp_model
from ortools.linear_solver import pywraplp
import pprint 

def solve_scheduling_with_routing(jobs, technicians, distance_matrix):
    """
    Solves a scheduling problem with OR-Tools to minimize total distance
    driven and maximize technician utilization.

    Args:
    - jobs (list): A list of jobs, each with attributes `id`, `location`, `duration`, `skill`.
    - technicians (list): A list of technicians, each with attributes `id`, `skills`, `max_hours`, `home_base`.
    - distance_matrix (list of lists): A matrix where element [i][j] is the distance between locations i and j.
                                     First N elements are job locations, followed by home base locations.
    """
    model = cp_model.CpModel()

    num_jobs = len(jobs)
    num_technicians = len(technicians)

    # Decision variables
    x = {}  # x[j, t] = 1 if job j is assigned to technician t
    for j in range(num_jobs):
        for t in range(num_technicians):
            x[j, t] = model.NewBoolVar(f'x[{j},{t}]')

    # Auxiliary variables for routing
    routes = {}  # routes[t, i, j] = 1 if technician t travels from job i to job j
    for t in range(num_technicians):
        for i in range(num_jobs):
            for j in range(num_jobs):
                if i != j:
                    routes[t, i, j] = model.NewBoolVar(f'routes[{t},{i},{j}]')

    # Add new variables for job start times
    start_times = {}
    for j in range(num_jobs):
        start_times[j] = model.NewIntVar(0, 480, f'start_time_{j}')  # 480 minutes = 8 hours

    # Add variables for job sequence
    is_first = {}  # is_first[j,t] = 1 if job j is first in technician t's route
    for j in range(num_jobs):
        for t in range(num_technicians):
            is_first[j,t] = model.NewBoolVar(f'is_first_{j}_{t}')

    # Add variables for home base connections
    start_route = {}  # start_route[t,j] = 1 if technician t starts their route with job j
    end_route = {}    # end_route[t,j] = 1 if technician t ends their route with job j
    for t in range(num_technicians):
        for j in range(num_jobs):
            start_route[t,j] = model.NewBoolVar(f'start_route[{t},{j}]')
            end_route[t,j] = model.NewBoolVar(f'end_route[{t},{j}]')

    # Constraints
    # Each job must be assigned to exactly one technician
    for j in range(num_jobs):
        model.Add(sum(x[j, t] for t in range(num_technicians)) == 1)

    # Technician capacity (time-based)
    for t in range(num_technicians):
        model.Add(
            sum(x[j, t] * jobs[j]['duration'] for j in range(num_jobs)) <= technicians[t]['max_hours']
        )

    # Skill matching: A technician can only be assigned a job if they have the required skills
    for j in range(num_jobs):
        for t in range(num_technicians):
            if jobs[j]['skill'] not in technicians[t]['skills']:
                model.Add(x[j, t] == 0)

    # Link routes and assignments: A technician can only travel between two jobs if they are assigned both
    for t in range(num_technicians):
        for i in range(num_jobs):
            for j in range(num_jobs):
                if i != j:
                    model.Add(routes[t, i, j] <= x[i, t])
                    model.Add(routes[t, i, j] <= x[j, t])

    # Route continuity constraints
    for t in range(num_technicians):
        # Each technician must start with exactly one job if they have any assignments
        model.Add(sum(start_route[t,j] for j in range(num_jobs)) == 
                 sum(x[j,t] for j in range(num_jobs)))
        
        # Each technician must end with exactly one job if they have any assignments
        model.Add(sum(end_route[t,j] for j in range(num_jobs)) == 
                 sum(x[j,t] for j in range(num_jobs)))
        
        for j in range(num_jobs):
            # Flow conservation: incoming + start = outgoing + end
            model.Add(
                sum(routes[t,i,j] for i in range(num_jobs) if i != j) + start_route[t,j] ==
                sum(routes[t,j,k] for k in range(num_jobs) if k != j) + end_route[t,j]
            )
            
            # Link assignments to route starts/ends
            model.Add(start_route[t,j] <= x[j,t])
            model.Add(end_route[t,j] <= x[j,t])

    # Time sequence constraints
    big_m = 1000  # Large constant for time window constraints
    for t in range(num_technicians):
        for j in range(num_jobs):
            # Add travel time from home base for first job
            model.Add(
                start_times[j] >= distance_matrix[technicians[t]['home_base']][j]
            ).OnlyEnforceIf(start_route[t,j])

        for i in range(num_jobs):
            for j in range(num_jobs):
                if i != j:
                    # If route i->j exists, ensure start_times are sequential
                    model.Add(
                        start_times[j] >= start_times[i] + jobs[i]['duration'] + 
                        distance_matrix[i][j]
                    ).OnlyEnforceIf(routes[t,i,j])

    # First job starts at time 0
    for t in range(num_technicians):
        for j in range(num_jobs):
            model.Add(start_times[j] == 0).OnlyEnforceIf(is_first[j,t])

    # Objective: Minimize total distance while maximizing utilization
    total_distance = sum(
        routes[t, i, j] * distance_matrix[i][j]
        for t in range(num_technicians)
        for i in range(num_jobs)
        for j in range(num_jobs)
        if i != j
    ) + sum(
        start_route[t,j] * distance_matrix[technicians[t]['home_base']][j]
        for t in range(num_technicians)
        for j in range(num_jobs)
    ) + sum(
        end_route[t,j] * distance_matrix[j][technicians[t]['home_base']]
        for t in range(num_technicians)
        for j in range(num_jobs)
    )
    total_utilization = sum(
        x[j, t] * jobs[j]['duration'] for t in range(num_technicians) for j in range(num_jobs)
    )
    model.Maximize(total_utilization - 0.1 * total_distance)  # Prioritize utilization with distance as a penalty

    # Solve the problem
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Parse the solution
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        solution = {'assignments': {}, 'routes': {}, 'schedule': {}}
        
        # Parse assignments
        for j in range(num_jobs):
            for t in range(num_technicians):
                if solver.Value(x[j, t]):
                    solution['assignments'][jobs[j]['id']] = technicians[t]['id']
                    solution['schedule'][jobs[j]['id']] = solver.Value(start_times[j])

        # Parse routes with home base
        for t in range(num_technicians):
            tech_id = technicians[t]['id']
            solution['routes'][tech_id] = []
            
            # Find the first job
            first_job = None
            for j in range(num_jobs):
                if solver.Value(start_route[t,j]):
                    first_job = j
                    break
            
            # Reconstruct the route including home base
            if first_job is not None:
                # Add home base start
                solution['routes'][tech_id].append(('home', first_job))
                
                current_job = first_job
                while True:
                    next_job = None
                    for j in range(num_jobs):
                        if j != current_job and solver.Value(routes[t,current_job,j]):
                            next_job = j
                            solution['routes'][tech_id].append((current_job, j))
                            break
                    if next_job is None:
                        # Add return to home base
                        for j in range(num_jobs):
                            if solver.Value(end_route[t,j]):
                                solution['routes'][tech_id].append((j, 'home'))
                        break
                    current_job = next_job

        return solution
    else:
        return "No feasible solution found."

# Example Usage
jobs = [
    {'id': 0, 'location': 0, 'duration': 2, 'skill': 'electrician'},
    {'id': 1, 'location': 1, 'duration': 3, 'skill': 'plumber'},
    {'id': 2, 'location': 2, 'duration': 1, 'skill': 'electrician'},
]

technicians = [
    {'id': 'tech1', 'skills': ['electrician'], 'max_hours': 5, 'home_base': 3},
    {'id': 'tech2', 'skills': ['plumber', 'electrician'], 'max_hours': 8, 'home_base': 4},
]

# Extended distance matrix to include home bases
distance_matrix = [
    # Jobs 0-2        Home bases
    [0, 10, 20,      15, 25],  # Job 0
    [10, 0, 15,      20, 30],  # Job 1
    [20, 15, 0,      25, 35],  # Job 2
    [15, 20, 25,     0, 40],   # Home base for tech1
    [25, 30, 35,     40, 0],   # Home base for tech2
]

solution = solve_scheduling_with_routing(jobs, technicians, distance_matrix)
pprint.pprint(solution)