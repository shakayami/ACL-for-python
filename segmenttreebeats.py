class SegmentTreeBeats:
    N=10003
    INF=10**18
    n=1;n0=1
    MAX_V=[0]*(4*N)
    SMAX_V=[0]*(4*N)
    SUM=[0]*(4*N)
    MAX_C=[0]*(4*N)
    def update_node_max(self,k,x):
        self.SUM[k]+=(x-self.MAX_V[k])*self.MAX_C[k]
        self.MAX_V[k]=x
    def push(self,k):
        if (self.MAX_V[k]<self.MAX_V[2*k+1]):
            self.update_node_max(2*k+1,self.MAX_V[k])
        if (self.MAX_V[k]<self.MAX_V[2*k+2]):
            self.update_node_max(2*k+2,self.MAX_V[k])
    def update(self,k):
        self.SUM[k]=self.SUM[2*k+1]+self.SUM[2*k+2]
        if (self.MAX_V[2*k+1]<self.MAX_V[2*k+2]):
            self.MAX_V[k]=self.MAX_V[2*k+2]
            self.MAX_C[k]=self.MAX_C[2*k+2]
            self.SMAX_V[k]=max(self.MAX_V[2*k+1],self.SMAX_V[2*k+2])
        elif (self.MAX_V[2*k+1]>self.MAX_V[2*k+2]):
            self.MAX_V[k]=self.MAX_V[2*k+1]
            self.MAX_C[k]=self.MAX_C[2*k+1]
            self.SMAX_V[k]=max(self.SMAX_V[2*k+1],self.MAX_V[2*k+2])
        else:
            self.MAX_V[k]=self.MAX_V[2*k+1]
            self.MAX_C[k]=self.MAX_C[2*k+1]+self.MAX_C[2*k+2]
            self.SMAX_V[k]=max(self.SMAX_V[2*k+1],self.SMAX_V[2*k+2])
    def _update_min(self,x,a,b,k,l,r):
        if (b<=l or r<=a or self.MAX_V[k]<=x):
            return
        if (a<=l and r<=b and self.SMAX_V[k]<x):
            self.update_node_max(k,x)
            return
        self.push(k)
        self._update_min(x,a,b,2*k+1,l,(l+r)//2)
        self._update_min(x,a,b,2*k+2,(l+r)//2,r)
        self.update(k)
    def _query_max(self,a,b,k,l,r):
        if(b<=l or r<=a):
            return 0
        if (a<=l and r<=b):
            return self.MAX_V[k]
        self.push(k)
        lv=self._query_max(a,b,2*k+1,l,(l+r)//2)
        rv=self._query_max(a,b,2*k+2,(l+r)//2,r)
        return max(lv,rv)
    def _query_sum(self,a,b,k,l,r):
        if(b<=l or r<=a):
            return 0
        if (a<=l and r<=b):
            return self.SUM[k]
        self.push(k)
        lv=self._query_sum(a,b,2*k+1,l,(l+r)//2)
        rv=self._query_sum(a,b,2*k+2,(l+r)//2,r)
        return lv+rv
    def __init__(self,n,a):
        self.n=n
        self.n0=1
        while(self.n0<n):self.n0<<=1
        for i in range(self.n):
            self.MAX_V[self.n0-1+i]=a[i]
            self.SUM[self.n0-1+i]=a[i]
            self.MAX_C[self.n0-1+i]=1
            self.SMAX_V[self.n0-1+i]=-self.INF
        for i in range(self.n,self.n0):
            self.MAX_V[self.n0-1+i]=-self.INF
            self.SMAX_V[self.n0-1+i]=-self.INF
            self.SUM[self.n0-1+i]=0
            self.MAX_C[self.n0-1+i]=0
        for i in range(self.n0-2,-1,-1):
            self.update(i)
    def update_min(self,a,b,x):
        return _update_min(x,a,b,0,0,self.n0)
    def query_max(self,a,b):
        return _query_max(a,b,0,0,self.n0)
    def query_sum(self,a,b):
        return _query_sum(a,b,0,0,self.n0)
