from collections import deque
class mf_graph:
    n=0
    g=[]
    def __init__(self,n_):
        self.n=n_
        self.g=[[] for i in range(self.n)]
        self.pos=[]
    class _edge:
        to=0
        rev=0
        cap=0
        def __init__(self,to_,rev_,cap_):
            self.to=to_
            self.rev=rev_
            self.cap=cap_
    class edge:
        From=0
        To=0
        Cap=0
        Flow=0
        def __init__(self,from_,to_,cap_,flow_):
            self.From=from_
            self.To=to_
            self.Cap=cap_
            self.Flow=flow_
    def add_edge(self,From_,To_,Cap_):
        assert 0<=From_ and From_<self.n
        assert 0<=To_ and To_<self.n
        assert 0<=Cap_
        m=len(self.pos)
        self.pos.append((From_,len(self.g[From_])))
        from_id=len(self.g[From_])
        to_id=len(self.g[To_])
        if (From_==To_):to_id+=1
        self.g[From_].append(self._edge(To_,to_id,Cap_))
        self.g[To_].append(self._edge(From_,from_id,0))
        return m
    def get_edge(self,i):
        m=len(self.pos)
        assert 0<=i and i<m
        _e=self.g[self.pos[i][0]][self.pos[i][1]]
        _re=self.g[_e.to][_e.rev]
        return self.edge(self.pos[i][0],_e.to,_e.cap+_re.cap,_re.cap)
    def edges(self,isdict=True):
        m=len(self.pos)
        result=[]
        for i in range(m):
            if isdict:
                e=self.get_edge(i)
                result.append({"from":e.From,"to":e.To,"cap":e.Cap,"flow":e.Flow})
            else:
                result.append(self.get_edge(i))
        return result
    def change_edge(self,i,new_cap,new_flow):
        m=len(self.pos)
        assert 0<=i and i<m
        assert 0<=new_flow and new_flow<=new_cap
        _e=self.g[pos[i][0]][pos[i][1]]
        _re=self.g[_e.to][_e.rev]
        _e.cap=new_cap-new_flow
        _re.cap=new_flow
        assert id(_e)==id(self.g[self.pos[i][0]][self.pos[i][1]])
        assert id(_re)==id(self.g[_e.to][_e.rev])
    def flow(self,s,t,flow_limit=(1<<63)-1):
        assert 0<=s and s<self.n
        assert 0<=t and t<self.n
        assert s!=t
        level=[0 for i in range(self.n)]
        Iter=[0 for i in range(self.n)]
        que=deque([])
        def bfs():
            for i in range(self.n):
                level[i]=-1
            level[s]=0
            que.clear()
            que.append(s)
            while(que):
                v=que.popleft()
                for e in self.g[v]:
                    if e.cap==0 or level[e.to]>=0:
                        continue
                    level[e.to]=level[v]+1
                    if (e.to==t):
                        return
                    que.append(e.to)
                
        def dfs(v,up):
            if v==s:return up
            res=0
            level_v=level[v]
            for i in range(Iter[v],len(self.g[v])):
                e=self.g[v][i]
                assert id(e)==id(self.g[v][i])
                if level_v<=level[e.to] or self.g[e.to][e.rev].cap==0:
                    continue
                d=dfs(e.to,min(up-res,self.g[e.to][e.rev].cap))
                if d<=0:continue
                self.g[v][i].cap+=d
                self.g[e.to][e.rev].cap-=d
                res+=d
                if (res==up):
                    return res
            level[v]=self.n
            return res
        flow=0
        while(flow<flow_limit):
            bfs()
            if level[t]==-1:
                break
            Iter=[0 for i in range(self.n)]
            f=dfs(t,flow_limit-flow)
            if not(f):
                break
            flow+=f
        return flow
    def min_cut(self,s):
        visited=[False for i in range(self.n)]
        que=deque([s])
        while(que):
            p=que.popleft()
            visited[p]=True
            for e in self.g[p]:
                if e.cap and not(visited[e.to]):
                    visited[e.to]=True
                    que.append(e.to)
        return visited
