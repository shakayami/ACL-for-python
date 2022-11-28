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
        if type(other)==int:
            ret=[(x*other)%self.mod for x in self.Func]
            return FPS(ret)
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
        if type(other)==int:
            invother=pow(other,self.mod-2,self.mod)
            ret=[(x*invother)%self.mod for x in self.Func]
            return FPS(ret)
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
    def diff(self):
        n=len(self.Func)
        ret=[0 for i in range(max(0,n-1))]
        for i in range(1,n):
            ret[i-1]=(self.Func[i]*i)%self.mod
        return FPS(ret)
    def integral(self):
        n=len(self.Func)
        ret=[0 for i in range(n+1)]
        for i in range(n):
            ret[i+1]=self.Func[i]*pow(i+1,self.mod-2,self.mod)%self.mod
        return FPS(ret)
    def log(self,deg=-1):
        assert self.Func[0]==1
        n=len(self.Func)
        if deg==-1:deg=n
        return (self.diff()*self.inv()).integral()
    def mod_sqrt(self,a):
        p=self.mod
        assert 0<=a and a<p
        if a<2:return a
        if pow(a,(p-1)//2,p)!=1:return -1
        b=1;one=1
        while(pow(b,(p-1)>>1,p)==1):
            b+=one
        m=p-1;e=0
        while(m%2==0):
            m>>=1
            e+=1
        x=pow(a,(m-1)>>1,p)
        y=(a*x*x)%p
        x*=a;
        x%=p
        z=pow(b,m,p)
        while(y!=1):
            j=0
            t=y
            while(t!=one):
                j+=1
                t*=t
                t%=p
            z=pow(z,1<<(e-j-1),p)
            x*=z
            x%=p
            z*=z
            z%=p
            y*=z
            y%=p
            e=j
        return x
    def sqrt(self,deg=-1):
        n=len(self.Func)
        if deg==-1:deg=n
        if n==0:return FPS([0 for i in range(deg)])
        if self.Func[0]==0:
            for i in range(1,n):
                if self.Func[i]!=0:
                    if i&1:return FPS([])
                    if deg-i//2<=0:break
                    ret=(self>>i).sqrt(deg-i//2)
                    if len(ret.Func)==0:return FPS([])
                    ret=ret<<(i//2)
                    if len(ret.Func)<deg:
                        ret.Func+=[0]*(deg-len(ret.Func))
                    return ret
            return FPS([0]*deg)
        sqr=self.mod_sqrt(self.Func[0])
        if sqr==-1:return FPS([])
        assert sqr*sqr%self.mod==self.Func[0]
        ret=FPS([sqr])
        inv2=(self.mod+1)//2
        i=1
        while(i<deg):
            ret=(ret+FPS(self.Func[:i<<1])*ret.inv(i<<1))*inv2
            i<<=1
        return FPS(ret.Func[:deg])
    def resize(self,deg):
        if len(self.Func)<deg:
            return FPS(self.Func+[0]*(deg-len(self.Func)))
        elif len(self.Func)>deg:
            return FPS(self.Func[:deg])
        else:
            return self
    def exp(self,deg=-1):
        n=len(self.Func)
        assert n>0 and self.Func[0]==0
        if deg==-1:deg=n
        assert deg>=0
        g=[1]
        g_fft=[1,1]
        self.Func[0]=1
        self.resize(deg)
        h_drv=self.diff()
        m=2
        while(m<deg):
            f_fft=self.Func[:m]+[0]*m
            self.butterfly(f_fft)
            
            #step 2.a
            _g=[f_fft[i]*g_fft[i]%self.mod for i in range(m)]
            self.butterfly_inv(_g)
            _g=_g[m//2:m]+[0]*(m//2)
            self.butterfly(_g)
            for i in range(m):
                _g[i]*=g_fft[i]
                _g[i]%=self.mod
            self.butterfly_inv(_g)
            tmp=pow(-m*m,self.mod-2,self.mod)
            for i in range(m):
                _g[i]*=tmp
                _g[i]%=self.mod
            g+=_g[:m//2]
            #step 2.b--2.d
            t=FPS(self.Func[:m]).diff()
            r=h_drv.Func[:m-1]+[0]
            self.butterfly(r)
            for i in range(m):
                r[i]*=f_fft[i]
                r[i]%=self.mod
            self.butterfly_inv(r)
            tmp=pow(-m,self.mod-2,self.mod)
            for i in range(m):
                r[i]*=tmp
                r[i]%=self.mod
            t=(t+FPS(r)).Func
            t=[t[-1]]+t
            t.pop()
            #step 2.e
            if (2*m<deg):
                if len(t)<2*m:
                    t+=[0]*(2*m-len(t))
                elif len(t)>2*m:
                    t=t[:2*m]
                self.butterfly(t)
                g_fft=g[:]
                if len(g_fft)<2*m:
                    g_fft+=[0]*(2*m-len(g_fft))
                elif len(g_fft)>2*m:
                    g_fft=g_fft[:2*m]
                self.butterfly(g_fft)
                for i in range(2*m):
                    t[i]*=g_fft[i]
                    t[i]%=self.mod
                self.butterfly_inv(t)
                tmp=pow(2*m,self.mod-2,self.mod)
                t=t[:m]
                for i in range(m):
                    t[i]*=tmp
                    t[i]%=self.mod
            else:
                g1=g[m//2:]
                s1=t[m//2:]
                t=t[:m//2]
                g1+=[0]*(m-len(g1))
                s1+=[0]*(m-len(s1))
                t+=[0]*(m-len(t))
                
                self.butterfly(g1)
                self.butterfly(t)
                self.butterfly(s1)
                for i in range(m):
                    s1[i]=(g_fft[i]*s1[i]+g1[i]*t[i])%self.mod
                for i in range(m):
                    t[i]*=g_fft[i]
                    t[i]%=self.mod
                self.butterfly_inv(t)
                self.butterfly_inv(s1)
                for i in range(m//2):
                    t[i+m//2]+=s1[i]
                    t[i+m//2]%=self.mod
                tmp=pow(m,self.mod-2,self.mod)
                for i in range(m):
                    t[i]*=tmp
                    t[i]%=self.mod
            #step 2.f
            v=self.Func[m:min(deg,2*m)]+[0]*(2*m-min(deg,2*m))
            t=[0]*(m-1)+t
            t=FPS(t).integral().Func
            for i in range(m):
                v[i]-=t[m+i]
                v[i]%=self.mod
            #step 2.g
            if len(v)<2*m:
                v+=[0]*(2*m-len(v))
            else:
                v=v[:2*m]
            self.butterfly(v)
            for i in range(2*m):
                v[i]*=f_fft[i]
                v[i]%=self.mod
            self.butterfly_inv(v)
            v=v[:m]
            tmp=pow(2*m,self.mod-2,self.mod)
            for i in range(m):
                v[i]*=tmp
                v[i]%=self.mod
            #step 2.h
            for i in range(min(deg-m,m)):
                self.Func[m+i]=v[i]
            m*=2
        return self
    def powfps(self,k,deg=-1):
        a=self.Func[:]
        n=len(self.Func)
        l=0
        while(l<len(a) and not a[l]):
            l+=1
        if l*k>=n:
            return FPS([0]*n)
        if l==len(a):
            return FPS([int(i==0) for i in range(n)])
        ic=pow(a[l],self.mod-2,self.mod)
        pc=pow(a[l],k,self.mod)
        a=FPS([(a[i]*ic)%self.mod for i in range(l,len(a))]).log()
        a*=k
        a=a.exp()
        a*=pc
        a=[0]*(l*k)+a.Func[:n-l*k]
        return FPS(a)
