import itertools

def manhattan(p1,p2): return abs(p1[0]-p2[0])+abs(p1[1]-p2[1])

def backtracking_csp(rovers,sites,cost_fn=manhattan):
    best_assign,best_cost=None,float("inf")
    for perm in itertools.permutations(sites,len(sites)):
        assign={i:[] for i in range(len(rovers))}; total=0
        for idx,site in enumerate(perm):
            r=idx%len(rovers); assign[r].append(site)
            total+=cost_fn(rovers[r],site)
        if total<best_cost: best_cost,best_assign=total,assign
    return best_assign,best_cost
