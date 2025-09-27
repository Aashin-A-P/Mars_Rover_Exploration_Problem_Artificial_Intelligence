import itertools

# =============================
# Simple Distance Function
# =============================
def manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


# =============================
# CSP Solver (Backtracking)
# =============================
def backtracking_csp(rovers, sites, cost_fn=manhattan):
    """
    Assign each site to one rover without overlap.

    rovers   : list of rover starting positions [(x,y), (x,y), ...]
    sites    : list of site positions [(x,y), (x,y), ...]
    cost_fn  : function to compute cost between rover and site

    Returns: dict {rover_index: assigned_sites}, total_cost
    """
    best_assignment = None
    best_cost = float("inf")

    # All possible assignments (permutations)
    for perm in itertools.permutations(sites, len(sites)):
        assignment = {i: [] for i in range(len(rovers))}
        total_cost = 0

        for site_idx, site in enumerate(perm):
            rover_idx = site_idx % len(rovers)  # round-robin assignment
            assignment[rover_idx].append(site)
            total_cost += cost_fn(rovers[rover_idx], site)

        if total_cost < best_cost:
            best_cost = total_cost
            best_assignment = assignment

    return best_assignment, best_cost


# =============================
# Example Usage
# =============================
if __name__ == "__main__":
    rovers = [(0, 0), (4, 4)]          # Rover 1 at (0,0), Rover 2 at (4,4)
    sites = [(1, 2), (3, 1), (2, 3)]   # Scientific sites

    assignment, cost = backtracking_csp(rovers, sites)

    print("Best Assignment:", assignment)
    print("Total Cost:", cost)
