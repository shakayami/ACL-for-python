'''
ACLにはないけど形式的べき級数ライブラリを作ってみる
とりあえずmod998244353限定で作ってみる
verifyはyosupo judgeを使いましょう。
'''
class FPS:
    sum_e=(911660635, 509520358, 369330050, 332049552, 983190778, 123842337, 238493703, 975955924, 603855026, 856644456, 131300601, 842657263, 730768835, 942482514, 806263778, 151565301, 510815449, 503497456, 743006876, 741047443, 56250497)
    sum_ie=(86583718, 372528824, 373294451, 645684063, 112220581, 692852209, 155456985, 797128860, 90816748, 860285882, 927414960, 354738543, 109331171, 293255632, 535113200, 308540755, 121186627, 608385704, 438932459, 359477183, 824071951)
    mod=998244353
    g=3
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
    def convolution(self,a,b):
        n=len(a);m=len(b)
        if not(a) or not(b):
            return []
        if min(n,m)<=40:
            if n<m:
                n,m=m,n
                a,b=b,a
            res=[0]*(n+m-1)
            for i in range(n):
                for j in range(m):
                    res[i+j]+=a[i]*b[j]
                    res[i+j]%=self.mod
            return res
        z=1<<((n+m-2).bit_length())
        a=a+[0]*(z-n)
        b=b+[0]*(z-m)
        self.butterfly(a)
        self.butterfly(b)
        c=[0]*z
        for i in range(z):
            c[i]=(a[i]*b[i])%self.mod
        self.butterfly_inv(c)
        iz=pow(z,self.mod-2,self.mod)
        for i in range(n+m-1):
            c[i]=(c[i]*iz)%self.mod
        return c[:n+m-1]
'''
convolutionの使用例
これでも本家ACLより速い（sum_e,sum_ieを作る分だけ速くなる）
N,M=map(int,input().split())
A=[int(i) for i in input().split()]
B=[int(i) for i in input().split()]
C=FPS().convolution(A,B)
print(*C)
'''
