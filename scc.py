def scc(N,edges):
    M=len(edges)
    start=[0]*(N+1)
    elist=[0]*M
    for e in edges:
        start[e[0]+1]+=1
    for i in range(1,N+1):
        start[i]+=start[i-1]
    counter=start[:]
    for e in edges:
        elist[counter[e[0]]]=e[1]
        counter[e[0]]+=1
    NG=[0,0]
    visited=[]
    low=[0]*N
    Ord=[-1]*N
    ids=[0]*N
    def dfs(v):
        low[v]=NG[0]
        Ord[v]=NG[0]
        NG[0]+=1
        visited.append(v)
        for i in range(start[v],start[v+1]):
            to=elist[i]
            if Ord[to]==-1:
                dfs(to)
                low[v]=min(low[v],low[to])
            else:
                low[v]=min(low[v],Ord[to])
        if low[v]==Ord[v]:
            while(True):
                u=visited.pop()
                Ord[u]=N
                ids[u]=NG[1]
                if u==v:
                    break
            NG[1]+=1
    for i in range(N):
        if Ord[i]==-1:
            dfs(i)
    for i in range(N):
        ids[i]=NG[1]-1-ids[i]
    group_num=NG[1]
    counts=[0]*group_num
    for x in ids:
        counts[x]+=1
    groups=[[] for i in range(group_num)]
    for i in range(N):
        groups[ids[i]].append(i)
    return groups
