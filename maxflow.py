import collections


class mf_graph:
    n = 0
    g = []

    def __init__(self, n_):
        self.n = n_
        self.g = [[] for i in range(self.n)]
        self.pos = []

    class _edge:
        to = 0
        rev = 0
        cap = 0

        def __init__(self, to_, rev_, cap_):
            self.to = to_
            self.rev = rev_
            self.cap = cap_

    class edge:
        From = 0
        To = 0
        Cap = 0
        Flow = 0

        def __init__(self, from_, to_, cap_, flow_):
            self.From = from_
            self.To = to_
            self.Cap = cap_
            self.Flow = flow_

    def add_edge(self, From_, To_, Cap_):
        assert 0 <= From_ and From_ < self.n
        assert 0 <= To_ and To_ < self.n
        assert 0 <= Cap_
        m = len(self.pos)
        self.pos.append((From_, len(self.g[From_])))
        from_id = len(self.g[From_])
        to_id = len(self.g[To_])
        if From_ == To_:
            to_id += 1
        self.g[From_].append(self._edge(To_, to_id, Cap_))
        self.g[To_].append(self._edge(From_, from_id, 0))
        return m

    def get_edge(self, i):
        m = len(self.pos)
        assert 0 <= i and i < m
        _e = self.g[self.pos[i][0]][self.pos[i][1]]
        _re = self.g[_e.to][_e.rev]
        return self.edge(self.pos[i][0], _e.to, _e.cap + _re.cap, _re.cap)

    def edges(self, isdict=True):
        m = len(self.pos)
        result = []
        for i in range(m):
            if isdict:
                e = self.get_edge(i)
                result.append(
                    {"from": e.From, "to": e.To, "cap": e.Cap, "flow": e.Flow}
                )
            else:
                result.append(self.get_edge(i))
        return result

    def change_edge(self, i, new_cap, new_flow):
        m = len(self.pos)
        assert 0 <= i and i < m
        assert 0 <= new_flow and new_flow <= new_cap
        _e = self.g[self.pos[i][0]][self.pos[i][1]]
        _re = self.g[_e.to][_e.rev]
        _e.cap = new_cap - new_flow
        _re.cap = new_flow
        assert id(_e) == id(self.g[self.pos[i][0]][self.pos[i][1]])
        assert id(_re) == id(self.g[_e.to][_e.rev])

    def flow(self, s, t, flow_limit=(1 << 63) - 1):
        assert 0 <= s and s < self.n
        assert 0 <= t and t < self.n
        assert s != t
        level = [0 for i in range(self.n)]
        Iter = [0 for i in range(self.n)]
        que = collections.deque([])

        def bfs():
            for i in range(self.n):
                level[i] = -1
            level[s] = 0
            que.clear()
            que.append(s)
            while que:
                v = que.popleft()
                for e in self.g[v]:
                    if e.cap == 0 or level[e.to] >= 0:
                        continue
                    level[e.to] = level[v] + 1
                    if e.to == t:
                        return
                    que.append(e.to)

        def dfs(s_, t_, up):
            # One call pushes a whole blocking flow for the current level
            # graph, so the caller runs one bfs() per phase rather than one per
            # augmenting path.  The search walks backwards from t_ to s_ along
            # residual edges, as ACL's recursive version does; g[v][i] is then
            # the reverse edge of the arc actually carrying the flow, and its
            # residual capacity lives in g[e.to][e.rev].cap.
            res = 0
            # path: (node, edge_index) from t_ towards s_, the current arc
            path = []
            v = t_
            while res < up:
                if v == s_:
                    # Bottleneck of the path, then push it in one sweep.
                    d = up - res
                    for node, i in path:
                        e = self.g[node][i]
                        rev_cap = self.g[e.to][e.rev].cap
                        if rev_cap < d:
                            d = rev_cap
                    for node, i in path:
                        e = self.g[node][i]
                        e.cap += d
                        self.g[e.to][e.rev].cap -= d
                    res += d
                    # Everything up to the first arc this saturated is still
                    # usable, so resume from there instead of restarting at t_.
                    k = 0
                    while k < len(path):
                        node, i = path[k]
                        e = self.g[node][i]
                        if self.g[e.to][e.rev].cap == 0:
                            break
                        k += 1
                    if k == len(path):
                        # Nothing saturated, so d was the remaining budget and
                        # res == up ends the loop.
                        break
                    v = path[k][0]
                    del path[k:]
                    continue
                # Advance the current arc of v past dead and saturated edges.
                g_v = self.g[v]
                level_v = level[v]
                i = Iter[v]
                while i < len(g_v):
                    e = g_v[i]
                    if level_v > level[e.to] and self.g[e.to][e.rev].cap > 0:
                        break
                    i += 1
                Iter[v] = i
                if i < len(g_v):
                    path.append((v, i))
                    v = g_v[i].to
                else:
                    # v can reach no unsaturated predecessor in this phase; the
                    # level marks it so no other path tries it again.
                    level[v] = self.n
                    if not path:
                        break
                    v, i = path.pop()
                    Iter[v] = i + 1
            return res

        flow = 0
        while flow < flow_limit:
            bfs()
            if level[t] == -1:
                break
            for i in range(self.n):
                Iter[i] = 0
            f = dfs(s, t, flow_limit - flow)
            if not (f):
                break
            flow += f
        return flow

    def min_cut(self, s):
        visited = [False for i in range(self.n)]
        que = collections.deque([s])
        while que:
            p = que.popleft()
            visited[p] = True
            for e in self.g[p]:
                if e.cap and not (visited[e.to]):
                    visited[e.to] = True
                    que.append(e.to)
        return visited
