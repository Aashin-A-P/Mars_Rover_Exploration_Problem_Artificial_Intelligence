from collections import defaultdict
from typing import List, Dict, Set, Optional

class CSP:
    def __init__(self, variables: List[str], domains: Dict[str, Set[str]], adj: Dict[str, Set[str]]):
        self.vars = variables
        self.domains = {v:set(domains[v]) for v in variables}
        self.adj = {v:set(adj.get(v,set())) for v in variables}

    def select_unassigned_var(self, assignment):  # MRV
        un = [v for v in self.vars if v not in assignment]
        return min(un, key=lambda v: len(self.domains[v]))

    def is_consistent(self, v, val, assignment):
        return all(assignment.get(n) != val for n in self.adj[v])

    def forward_check(self, v, val, assignment):
        pruned = defaultdict(set)
        for n in self.adj[v]:
            if n in assignment: continue
            for x in list(self.domains[n]):
                if x == val:
                    self.domains[n].remove(x)
                    pruned[n].add(x)
        return pruned

    def restore(self, pruned):
        for var, vals in pruned.items():
            self.domains[var] |= vals

    def backtrack_trace(self, assignment):
        trace = []
        def rec():
            if len(assignment) == len(self.vars):
                trace.append({"event":"solution","assignment":assignment.copy(),"selected":None,"tried":None,"pruned":{}})
                return True
            v = self.select_unassigned_var(assignment)
            trace.append({"event":"choose","assignment":assignment.copy(),"selected":v,"tried":None,"pruned":{}})
            for val in list(self.domains[v]):
                if not self.is_consistent(v, val, assignment):
                    trace.append({"event":"inconsistent","assignment":assignment.copy(),"selected":v,"tried":val,"pruned":{}})
                    continue
                assignment[v] = val
                pruned = self.forward_check(v, val, assignment)
                trace.append({"event":"assign","assignment":assignment.copy(),"selected":v,"tried":val,"pruned":{k:list(vs) for k,vs in pruned.items()}})
                if rec(): return True
                self.restore(pruned)
                assignment.pop(v, None)
                trace.append({"event":"backtrack","assignment":assignment.copy(),"selected":v,"tried":val,"pruned":{k:list(vs) for k,vs in pruned.items()}})
            return False
        rec()
        return trace
