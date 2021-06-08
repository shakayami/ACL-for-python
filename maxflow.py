from collections import deque
class mf_graph:
    n=1
    g=[[] for i in range(1)]
    pos=[]
    def __init__(self,N):
        self.n=N
        self.g=[[] for i in range(N)]
    def add_edge(self,From,To,cap):
        assert 0<=From and From<self.n
        assert 0<=To and To<self.n
        assert 0<=cap
        m=len(self.pos)
        self.pos.append((From,len(self.g[From])))
        self.g[From].append({"to":To,"rev":len(self.g[To]),"cap":cap})
        self.g[To].append({"to":From,"rev":len(self.g[From])-1,"cap":0})
        return m
    def get_edge(self,i):
        m=len(self.pos)
        assert 0<=i and i<m
        _e=self.g[self.pos[i][0]][self.pos[i][1]]
        _re=self.g[_e["to"]][_e["rev"]]
        return {"from":self.pos[i][0],
                "to":_e["to"],
                "cap":_e["cap"]+_re["cap"],
                "flow":_re["cap"]}
    def edges(self):
        m=len(self.pos)
        result=[]
        for i in range(m):
            result.append(self.get_edge(i))
        return result
    def change_edge(self,i,new_cap,new_flow):
        m=len(self.pos)
        assert 0<=i and i<m
        assert 0<=new_flow and new_flow<=new_cap
        _e=self.g[self.pos[i][0]][self.pos[i][1]]
        _re=self.g[_e["to"]][_e["rev"]]
        _e["cap"]=new_cap-new_flow
        _re["cap"]=new_flow
    def flow(self,s,t,flow_limit=(2**31)-1):
        assert 0<=s and s<self.n
        assert 0<=t and t<self.n
        level=[0 for i in range(self.n)]
        Iter=[0 for i in range(self.n)]
        que=deque([])
        def bfs():
            for i in range(self.n):level[i]=-1
            level[s]=0
            que=deque([])
            que.append(s)
            while(len(que)>0):
                v=que.popleft()
                for e in self.g[v]:
                    if e["cap"]==0 or level[e["to"]]>=0:continue
                    level[e["to"]]=level[v]+1
                    if e["to"]==t:return
                    que.append(e["to"])
        def dfs(func,v,up):
            if (v==s):return up
            res=0
            level_v=level[v]
            for i in range(Iter[v],len(self.g[v])):
                e=self.g[v][i]
                if (level_v<=level[e["to"]] or self.g[e["to"]][e["rev"]]["cap"]==0):continue
                d=func(func,e["to"],min(up-res,self.g[e["to"]][e["rev"]]["cap"]))
                if d<=0:continue
                self.g[v][i]["cap"]+=d
                self.g[e["to"]][e["rev"]]["cap"]-=d
                res+=d
                if res==up:return res
            level[v]=self.n
            return res
        flow=0
        while(flow<flow_limit):
            bfs()
            if level[t]==-1:break
            for i in range(self.n):Iter[i]=0
            while(flow<flow_limit):
                f=dfs(dfs,t,flow_limit-flow)
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
            for e in self.g[p]:
                if e["cap"] and not(visited[e["to"]]):
                    visited[e["to"]]=True
                    que.append(e["to"])
        return visited
