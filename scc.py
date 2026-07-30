def scc(N, edges):
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

    low = [0] * N
    Ord = [-1] * N
    ids = [0] * N
    visited = []
    now_ord = 0
    group_num = 0

    for root in range(N):
        if Ord[root] != -1:
            continue
        node_stack = [root]
        it_stack = [start[root + 1] - 1]
        low[root] = Ord[root] = now_ord
        now_ord += 1
        visited.append(root)
        while node_stack:
            v = node_stack[-1]
            i = it_stack[-1]
            if i >= start[v]:
                it_stack[-1] = i - 1
                to = elist[i]
                if Ord[to] == -1:
                    low[to] = Ord[to] = now_ord
                    now_ord += 1
                    visited.append(to)
                    node_stack.append(to)
                    it_stack.append(start[to + 1] - 1)
                elif Ord[to] < low[v]:
                    low[v] = Ord[to]
            else:
                node_stack.pop()
                it_stack.pop()
                if low[v] == Ord[v]:
                    while True:
                        u = visited.pop()
                        Ord[u] = N
                        ids[u] = group_num
                        if u == v:
                            break
                    group_num += 1
                if node_stack:
                    bef = node_stack[-1]
                    if low[v] < low[bef]:
                        low[bef] = low[v]

    for i in range(N):
        ids[i] = group_num - 1 - ids[i]
    groups = [[] for _ in range(group_num)]
    for i in range(N):
        groups[ids[i]].append(i)
    return groups
