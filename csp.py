import itertools

def manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def backtracking_csp(rovers, sites, cost_fn=manhattan):
    best_assignment = None
    best_cost = float("inf")
    for perm in itertools.permutations(sites, len(sites)):
        assignment = {i: [] for i in range(len(rovers))}
        total_cost = 0
        for site_idx, site in enumerate(perm):
            rover_idx = site_idx % len(rovers)
            assignment[rover_idx].append(site)
            total_cost += cost_fn(rovers[rover_idx], site)
        if total_cost < best_cost:
            best_cost, best_assignment = total_cost, assignment
    return best_assignment, best_cost
