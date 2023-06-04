from collections import deque
class mf_graph:
    n=1
    g=[[] for i in range(1)]
    pos=[]
    def __init__(self,N):
        self.n=N
        self.g=[[] for i in range(N)]
        self.pos=[]
    def add_edge(self,From,To,cap):
        assert 0<=From and From<self.n
        assert 0<=To and To<self.n
        assert 0<=cap
        m=len(self.pos)
        from_id=len(self.g[From])
        self.pos.append([From,from_id])
        to_id=len(self.g[To])
        if From==To:to_id+=1
        self.g[From].append([To,to_id,cap])
        self.g[To].append([From,from_id,0])
        return m
    def get_edge(self,i):
        m=len(self.pos)
        assert 0<=i and i<m
        _e=self.g[self.pos[i][0]][self.pos[i][1]]
        _re=self.g[_e[0]][_e[1]]
        return [self.pos[i][0],_e[0],_e[2]+_re[2],_re[2]]
    def edges(self):
        m=len(self.pos)
        result=[]
        for i in range(m):
            a,b,c,d=self.get_edge(i)
            result.append({"from":a,"to":b,"cap":c,"flow":d})
        return result

    def change_edge(self,i,new_cap,new_flow):
        m=len(self.pos)
        assert 0<=i and i<m
        assert 0<=new_flow and new_flow<=new_cap
        _e=self.g[self.pos[i][0]][self.pos[i][1]]
        _re=self.g[_e[0]][_e[1]]
        _e[2]=new_cap-new_flow
        _re[2]=new_flow
    def flow(self,s,t,flow_limit=(1<<63)-1):
        assert 0<=s and s<self.n
        assert 0<=t and t<self.n
        assert s!=t
        def bfs():
            level=[-1 for i in range(self.n)]
            level[s]=0
            que=deque([])
            que.append(s)
            while(que):
                v=que.popleft()
                for to,rev,cap in self.g[v]:
                    if cap==0 or level[to]>=0:continue
                    level[to]=level[v]+1
                    if to==t:return level
                    que.append(to)
            return level
        def dfs(v,up):
            if (v==s):return up
            res=0
            level_v=level[v]
            for i in range(Iter[v],len(self.g[v])):
                Iter[v]=i
                to,rev,cap=self.g[v][i]
                if (level_v<=level[to] or self.g[to][rev][2]==0):continue
                d=dfs(to,min(up-res,self.g[to][rev][2]))
                if d<=0:continue
                self.g[v][i][2]+=d
                self.g[to][rev][2]-=d
                res+=d
                if res==up:return res
            level[v]=self.n
            return res

        flow=0
        while(flow<flow_limit):
            level=bfs()
            if level[t]==-1:break
            Iter=[0 for i in range(self.n)]
            f=dfs(t,flow_limit-flow)
            if not(f):break
            flow+=f
        return flow
    def min_cut(self,s):
        visited=[False for i in range(self.n)]
        que=deque([])
        que.append(s)
        while(len(que)>0):
            p=que.popleft()
            visited[p]=True
            for to,rev,cap in self.g[p]:
                if cap and not(visited[to]):
                    visited[to]=True
                    que.append(to)
        return visited
