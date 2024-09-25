class dsu():
    n=1
    parent_or_size=[-1 for i in range(n)]
    def __init__(self,N):
        self.n=N
        self.parent_or_size=[-1 for i in range(N)]
    def merge(self,a,b):
        assert 0<=a<self.n, "0<=a<n,a={0},n={1}".format(a,self.n)
        assert 0<=b<self.n, "0<=b<n,b={0},n={1}".format(b,self.n)
        x=self.leader(a)
        y=self.leader(b)
        if x==y:
            return x
        if (-self.parent_or_size[x]<-self.parent_or_size[y]):
            x,y=y,x
        self.parent_or_size[x]+=self.parent_or_size[y]
        self.parent_or_size[y]=x
        return x
    def same(self,a,b):
        assert 0<=a<self.n, "0<=a<n,a={0},n={1}".format(a,self.n)
        assert 0<=b<self.n, "0<=b<n,b={0},n={1}".format(b,self.n)
        return self.leader(a)==self.leader(b)
    def leader(self,a):
        assert 0<=a<self.n, "0<=a<n,a={0},n={1}".format(a,self.n)
        if (self.parent_or_size[a]<0):
            return a
        self.parent_or_size[a]=self.leader(self.parent_or_size[a])
        return self.parent_or_size[a]
    def size(self,a):
        assert 0<=a<self.n, "0<=a<n,a={0},n={1}".format(a,self.n)
        return -self.parent_or_size[self.leader(a)]
    def groups(self):
        leader_buf=[0 for i in range(self.n)]
        group_size=[0 for i in range(self.n)]
        for i in range(self.n):
            leader_buf[i]=self.leader(i)
            group_size[leader_buf[i]]+=1
        result=[[] for i in range(self.n)]
        for i in range(self.n):
            result[leader_buf[i]].append(i)
        result2=[]
        for i in range(self.n):
            if len(result[i])>0:
                result2.append(result[i])
        return result2
