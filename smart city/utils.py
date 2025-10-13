import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional, Set

Grid = List[List[str]]
Pos = Tuple[int, int]
COST = {'.': 1, 't': 3, 'c': 5}

CELL_OPTIONS = ['.', 't', 'c', '#', 'S', 'D']
CELL_LABELS = {
    '.': 'Road (1)',
    't': 'Traffic (3)',
    'c': 'Construction (5)',
    '#': 'Wall',
    'S': 'Start',
    'D': 'Destination'
}

def parse_df_to_grid(df: pd.DataFrame) -> Tuple[Grid, Pos, Pos]:
    grid = df.astype(str).values.tolist()
    start = goal = (-1, -1)
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == 'S':
                start = (r, c); grid[r][c] = '.'
            elif ch == 'D':
                goal = (r, c); grid[r][c] = '.'
    if start == (-1, -1) or goal == (-1, -1):
        raise ValueError("Please place exactly one 'S' and one 'D' on the grid.")
    return grid, start, goal

def in_bounds(grid: Grid, p: Pos) -> bool:
    r, c = p
    return 0 <= r < len(grid) and 0 <= c < len(grid[0])

def neighbors4(p: Pos) -> List[Pos]:
    r, c = p
    return [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]

def cell_cost(ch: str) -> float:
    if ch == '#':
        return float('inf')
    return COST.get(ch, 1)

def reconstruct_path(prev: Dict[Pos, Pos], s: Pos, t: Pos) -> List[Pos]:
    path, cur = [], t
    while cur != s:
        path.append(cur)
        cur = prev[cur]
    path.append(s)
    path.reverse()
    return path

def path_cost(grid: Grid, path: Optional[List[Pos]]) -> Optional[float]:
    if not path: return None
    return sum(cell_cost(grid[r][c]) for (r, c) in (path[1:] if path else []))

def manhattan(a, b):
    """Calculate Manhattan distance between two grid cells."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

