import math
MOVES=[(-1,0),(1,0),(0,-1),(0,1)]

def is_valid(grid,x,y):
    rows,cols=len(grid),len(grid[0])
    return 0<=x<rows and 0<=y<cols and grid[x][y]!=1

def evaluate(sites,positions):
    scores=[0,0]
    for s in sites:
        if positions[0]==s: scores[0]+=1
        elif positions[1]==s: scores[1]+=1
    return scores[0]-scores[1]

def get_moves(grid,pos):
    return [(pos[0]+dx,pos[1]+dy) for dx,dy in MOVES if is_valid(grid,pos[0]+dx,pos[1]+dy)]

def minimax(grid,sites,positions,depth,alpha,beta,maximizing_player):
    if depth==0 or not sites: return evaluate(sites,positions),None
    best=None
    if maximizing_player==0:
        val=-math.inf
        for m in get_moves(grid,positions[0]):
            np=(m,positions[1]); ns=sites.copy()
            if m in ns: ns.remove(m)
            ev,_=minimax(grid,ns,np,depth-1,alpha,beta,1)
            if ev>val: val, best=ev,m
            alpha=max(alpha,ev); 
            if beta<=alpha: break
        return val,best
    else:
        val=math.inf
        for m in get_moves(grid,positions[1]):
            np=(positions[0],m); ns=sites.copy()
            if m in ns: ns.remove(m)
            ev,_=minimax(grid,ns,np,depth-1,alpha,beta,0)
            if ev<val: val,best=ev,m
            beta=min(beta,ev); 
            if beta<=alpha: break
        return val,best
