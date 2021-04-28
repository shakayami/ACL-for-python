'''
ACLにはないけど形式的べき級数ライブラリを作ってみる
とりあえずmod998244353限定で作ってみる
verifyはyosupo judgeを使いましょう。
'''
class FPS:
    sum_e=(911660635, 509520358, 369330050, 332049552, 983190778, 123842337, 238493703, 975955924, 603855026, 856644456, 131300601, 842657263, 730768835, 942482514, 806263778, 151565301, 510815449, 503497456, 743006876, 741047443, 56250497)
    sum_ie=(86583718, 372528824, 373294451, 645684063, 112220581, 692852209, 155456985, 797128860, 90816748, 860285882, 927414960, 354738543, 109331171, 293255632, 535113200, 308540755, 121186627, 608385704, 438932459, 359477183, 824071951)
    mod=998244353
    Func=[0]
    def __init__(self,L):
        self.Func=[x%self.mod for x in L]
    def butterfly(self,a):
        n=len(a)
        h=(n-1).bit_length()
        for ph in range(1,h+1):
            w=1<<(ph-1)
            p=1<<(h-ph)
            now=1
            for s in range(w):
                offset=s<<(h-ph+1)
                for i in range(p):
                    l=a[i+offset]
                    r=a[i+offset+p]*now
                    r%=self.mod
                    a[i+offset]=l+r
                    a[i+offset]%=self.mod
                    a[i+offset+p]=l-r
                    a[i+offset+p]%=self.mod
                now*=self.sum_e[(~s & -~s).bit_length()-1]
                now%=self.mod
        return a
    def butterfly_inv(self,a):
        n=len(a)
        h=(n-1).bit_length()
        for ph in range(h,0,-1):
            w=1<<(ph-1)
            p=1<<(h-ph)
            inow=1
            for s in range(w):
                offset=s<<(h-ph+1)
                for i in range(p):
                    l=a[i+offset]
                    r=a[i+offset+p]
                    a[i+offset]=l+r
                    a[i+offset]%=self.mod
                    a[i+offset+p]=(l-r)*inow
                    a[i+offset+p]%=self.mod
                inow*=self.sum_ie[(~s & -~s).bit_length()-1]
                inow%=self.mod
        return a
    def __mul__(self,other):
        a=self.Func
        b=other.Func
        n=len(a);m=len(b)
        if not(a) or not(b):
            return FPS([])
        if min(n,m)<=40:
            if n<m:
                n,m=m,n
                a,b=b,a
            res=[0]*(n+m-1)
            for i in range(n):
                for j in range(m):
                    res[i+j]+=a[i]*b[j]
                    res[i+j]%=self.mod
            return FPS(res)
        z=1<<((n+m-2).bit_length())
        a=a+[0]*(z-n)
        b=b+[0]*(z-m)
        a=self.butterfly(a)
        b=self.butterfly(b)
        c=[0]*z
        for i in range(z):
            c[i]=(a[i]*b[i])%self.mod
        self.butterfly_inv(c)
        iz=pow(z,self.mod-2,self.mod)
        for i in range(n+m-1):
            c[i]=(c[i]*iz)%self.mod
        return FPS(c[:n+m-1])
    def __imul__(self,other):
        self=self*other
        return self
    def __add__(self,other):
        res=[0 for i in range(max(len(self.Func),len(other.Func)))]
        for i,x in enumerate(self.Func):
            res[i]+=x
            res[i]%=self.mod
        for i,x in enumerate(other.Func):
            res[i]+=x
            res[i]%=self.mod
        return FPS(res)
    def __iadd__(self,other):
        self=(self+other)
        return self
    def __sub__(self,other):
        res=[0 for i in range(max(len(self.Func),len(other.Func)))]
        for i,x in enumerate(self.Func):
            res[i]+=x
            res[i]%=self.mod
        for i,x in enumerate(other.Func):
            res[i]-=x
            res[i]%=self.mod
        return FPS(res)
    def __isub__(self,other):
        self=self-other
        return self
    def inv(self,d=-1):
        n=len(self.Func)
        assert n!=0 and self.Func[0]!=0
        if d==-1:d=n
        assert d>0
        res=[pow(self.Func[0],self.mod-2,self.mod)]
        while(len(res)<d):
            m=len(res)
            f=[self.Func[i] for i in range(min(n,2*m))]
            r=res[:]

            if len(f)<2*m:
                f+=[0]*(2*m-len(f))
            elif len(f)>2*m:
                f=f[:2*m]
            if len(r)<2*m:
                r+=[0]*(2*m-len(r))
            elif len(r)>2*m:
                r=r[:2*m]
            f=self.butterfly(f)
            r=self.butterfly(r)
            for i in range(2*m):
                f[i]*=r[i]
                f[i]%=self.mod
            f=self.butterfly_inv(f)
            f=f[m:]
            if len(f)<2*m:
                f+=[0]*(2*m-len(f))
            elif len(f)>2*m:
                f=f[:2*m]
            f=self.butterfly(f)
            for i in range(2*m):
                f[i]*=r[i]
                f[i]%=self.mod
            f=self.butterfly_inv(f)
            iz=pow(2*m,self.mod-2,self.mod)
            iz*=-iz
            iz%=self.mod
            for i in range(m):
                f[i]*=iz
                f[i]%=self.mod
            res+=f[:m]
        return FPS(res[:d])
    def __truediv__(self,other):
        assert (other.Func[0]!=0)
        return self*(other.inv())
    def __itruediv__(self,other):
        self=self/other
        return self
    def __lshift__(self,d):
        n=len(self.Func)
        self.Func=[0]*d+self.Func
        return FPS(self.Func[:n])
    def __ilshift__(self,d):
        self=self<<d
        return self
    def __rshift__(self,d):
        n=len(self.Func)
        self.Func=self.Func[min(n,d):]
        self.Func+=[0]*(n-len(self.Func))
        return FPS(self.Func)
    def __irshift__(self,d):
        self=self>>d
        return self
    def __str__(self):
        return f'FPS({self.Func})'

