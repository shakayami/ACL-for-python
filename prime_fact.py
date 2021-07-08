from math import gcd
import random
from collections import defaultdict
def is_prime(n):
    if n==2:
        return True
    if n==1 or n&1==0:
        return False
    d=(n-1)>>1
    while d&1==0:
        d>>=1

    for k in range(100):
        a=random.randint(1,n-1)
        t=d
        y=pow(a, t, n)
        while t!=n-1 and y!=1 and y!=n-1:
            y=(y*y)%n
            t<<=1
        if y!=n-1 and t&1==0:
            return False
    return True

def prime_fact(N):
    res=defaultdict(int)
    if N==1:
        return res
    p=2
    while(p<=10**4 and N>1):
        if N%p==0:
            while(N%p==0):
                res[p]+=1
                N//=p
        p+=1
    while(N>1):
        if is_prime(N):
            res[N]+=1
            break
        x=random.randrange(N)
        y=(x*x+1)%N
        i=1
        while(True):
            d=gcd(abs(x-y),N)
            if d==1:
                i+=1
            elif d==N:
                res[N]+=1
                return res
            else:
                res[d]+=1
                N//=d
                break
            x=(x*x+1)%N
            y=(y*y+1)%N
            y=(y*y+1)%N
    return res
