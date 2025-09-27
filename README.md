# Mars_Rover_Exploration_Problem_Artificial_Intelligence
An AI project to demonstrate the major search strategies and problem solving strategies to solve the Mars Rover Problem


So we plan to implement a Mars Rover Exploration Project implementing
- DFS
- BFS
- A* algorithm
- UCS
- Adversial Search
- CSP

## 1. **Depth First Search (DFS)**

- **Idea:** Explore one route deeply before backtracking.
    
- **In Rover Context:**
    
    - The rover keeps driving in one direction until it either finds the site or hits a crater.
        
    - Risk: may waste time going into long dead ends.
        
- **Best When:** Memory is limited, and _any_ path is acceptable.
    

---

## 2. **Breadth First Search (BFS)**

- **Idea:** Expand all paths level by level.
    
- **In Rover Context:**
    
    - The rover explores all nearby squares first, ensuring it finds the path with **fewest steps**.
        
    - Doesn’t consider terrain difficulty or energy.
        
- **Best When:** Terrain cost is uniform, and you want the _shortest path in steps_.
    

---

## 3. **Uniform Cost Search (UCS)**

- **Idea:** Always expand the path with the **lowest cumulative cost so far**.
    
- **In Rover Context:**
    
    - Each move has a cost = energy usage (flat terrain = 1, rocky slope = 3, crater detour = 5, etc.).
        
    - UCS finds the **least energy-consuming path**, even if it’s longer in steps.
        
- **Strength:** Optimal when costs vary.
    
- **Weakness:** Can expand many unnecessary nodes if no heuristic is guiding it.
    
- **Best When:** Energy efficiency is more important than number of steps.
    

---

## 4. **Informed Search (A*)**

- **Idea:** Use both real cost and heuristic estimate.
    
- **Formula:** `f(n) = g(n) + h(n)`
    
    - `g(n)` = cost so far (like UCS)
        
    - `h(n)` = estimated cost to goal (distance, slope factor)
        
- **In Rover Context:**
    
    - A* prefers paths that are both energy-efficient and closer to the goal.
        
    - Much faster than UCS if heuristic is admissible.
        

---

## 5. **Constraint Satisfaction Problem (CSP)**

- **Idea:** Assign rovers to multiple targets under rules.
    
- **In Rover Context:**
    
    - Variables = sites of interest.
        
    - Domains = possible rovers.
        
    - Constraints = no overlapping paths, limited energy per rover, all sites covered.
        
    - Solvers: Backtracking, AC-3, MRV heuristic.
        
- **Best When:** Multiple rovers must coordinate missions efficiently.
    

---

## 6. **Adversarial Search (Game/Minimax)**

- **Idea:** Optimize strategy against an opponent.
    
- **In Rover Context:**
    
    - NASA rover vs ISRO rover racing to collect samples.
        
    - Turns alternate; evaluation function = sites collected difference.
        
    - Algorithm: Minimax with Alpha-Beta pruning.
        
- **Best When:** Missions are competitive, not cooperative.

