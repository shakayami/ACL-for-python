def two_sat(n, clause):
    answer = [0] * n
    edges = []
    N = 2 * n
    for s in clause:
        i, f, j, g = s
        edges.append((2 * i + (0 if f else 1), 2 * j + (1 if g else 0)))
        edges.append((2 * j + (0 if g else 1), 2 * i + (1 if f else 0)))
    M = len(edges)
    start = [0] * (N + 1)
    elist = [0] * M
    for e in edges:
        start[e[0] + 1] += 1
    for i in range(1, N + 1):
        start[i] += start[i - 1]
    counter = start[:]
    for e in edges:
        elist[counter[e[0]]] = e[1]
        counter[e[0]] += 1
    visited = []
    low = [0] * N
    Ord = [-1] * N
    ids = [0] * N
    NG = [0, 0]

    def dfs(v):
        stack = [(v, -1, 0), (v, -1, 1)]
        while stack:
            v, bef, t = stack.pop()
            if t:
                if bef != -1 and Ord[v] != -1:
                    low[bef] = min(low[bef], Ord[v])
                    stack.pop()
                    continue
                low[v] = NG[0]
                Ord[v] = NG[0]
                NG[0] += 1
                visited.append(v)
                for i in range(start[v], start[v + 1]):
                    to = elist[i]
                    if Ord[to] == -1:
                        stack.append((to, v, 0))
                        stack.append((to, v, 1))
                    else:
                        low[v] = min(low[v], Ord[to])
            else:
                if low[v] == Ord[v]:
                    while True:
                        u = visited.pop()
                        Ord[u] = N
                        ids[u] = NG[1]
                        if u == v:
                            break
                    NG[1] += 1
                low[bef] = min(low[bef], low[v])

    for i in range(N):
        if Ord[i] == -1:
            dfs(i)
    for i in range(N):
        ids[i] = NG[1] - 1 - ids[i]
    for i in range(n):
        if ids[2 * i] == ids[2 * i + 1]:
            return None
        answer[i] = ids[2 * i] < ids[2 * i + 1]
    return answer
