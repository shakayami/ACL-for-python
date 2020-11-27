import heapq
class mcf_graph():
    n=1
    pos=[]
    g=[[]]
    def __init__(self,N):
        self.n=N
        self.pos=[]
        self.g=[[] for i in range(N)]
    def add_edge(self,From,To,cap,cost):
        assert 0<=From and From<self.n
        assert 0<=To and To<self.n
        m=len(self.pos)
        self.pos.append((From,len(self.g[From])))
        self.g[From].append({"to":To,"rev":len(self.g[To]),"cap":cap,"cost":cost})
        self.g[To].append({"to":From,"rev":len(self.g[From])-1,"cap":0,"cost":-cost})
    def get_edge(self,i):
        m=len(self.pos)
        assert 0<=i and i<m
        _e=self.g[self.pos[i][0]][self.pos[i][1]]
        _re=self.g[_e["to"]][_e["rev"]]
        return {"from":self.pos[i][0],"to":_e["to"],"cap":_e["cap"]+_re["cap"],
        "flow":_re["cap"],"cost":_e["cost"]}
    def edges(self):
        m=len(self.pos)
        result=[{} for i in range(m)]
        for i in range(m):
            tmp=self.get_edge(i)
            result[i]["from"]=tmp["from"]
            result[i]["to"]=tmp["to"]
            result[i]["cap"]=tmp["cap"]
            result[i]["flow"]=tmp["flow"]
            result[i]["cost"]=tmp["cost"]
        return result
    def flow(self,s,t,flow_limit=(1<<63)-1):
        return self.slope(s,t,flow_limit)[-1]
    def slope(self,s,t,flow_limit=(1<<63)-1):
        assert 0<=s and s<self.n
        assert 0<=t and t<self.n
        assert s!=t
        '''
         variants (C = maxcost):
         -(n-1)C <= dual[s] <= dual[i] <= dual[t] = 0
         reduced cost (= e.cost + dual[e.from] - dual[e.to]) >= 0 for all edge
        '''
        dual=[0 for i in range(self.n)]
        dist=[0 for i in range(self.n)]
        pv=[0 for i in range(self.n)]
        pe=[0 for i in range(self.n)]
        vis=[False for i in range(self.n)]
        def dual_ref():
            for i in range(self.n):
                dist[i]=(1<<63)-1
                pv[i]=-1
                pe[i]=-1
                vis[i]=False
            que=[]
            heapq.heappush(que,(0,s))
            dist[s]=0
            while(que):
                v=heapq.heappop(que)[1]
                if vis[v]:continue
                vis[v]=True
                if v==t:break
                '''
                 dist[v] = shortest(s, v) + dual[s] - dual[v]
                 dist[v] >= 0 (all reduced cost are positive)
                 dist[v] <= (n-1)C
                '''
                for i in range(len(self.g[v])):
                    e=self.g[v][i]
                    if vis[e["to"]] or (not(e["cap"])):continue
                    '''
                     |-dual[e.to]+dual[v]| <= (n-1)C
                     cost <= C - -(n-1)C + 0 = nC
                    '''
                    cost=e["cost"]-dual[e["to"]]+dual[v]
                    if dist[e["to"]]-dist[v]>cost:
                        dist[e["to"]]=dist[v]+cost
                        pv[e["to"]]=v
                        pe[e["to"]]=i
                        heapq.heappush(que,(dist[e["to"]],e["to"]))
            if not(vis[t]):
                return False
            for v in range(self.n):
                if not(vis[v]):continue
                dual[v]-=dist[t]-dist[v]
            return True
        flow=0
        cost=0
        prev_cost=-1
        result=[(flow,cost)]
        while(flow<flow_limit):
            if not(dual_ref()):
                break
            c=flow_limit-flow
            v=t
            while(v!=s):
                c=min(c,self.g[pv[v]][pe[v]]["cap"])
                v=pv[v]
            v=t
            while(v!=s):
                self.g[pv[v]][pe[v]]["cap"]-=c
                self.g[v][self.g[pv[v]][pe[v]]["rev"]]["cap"]+=c
                v=pv[v]
            d=-dual[s]
            flow+=c
            cost+=c*d
            if(prev_cost==d):
                result.pop()
            result.append((flow,cost))
            prev_cost=cost
        return result
