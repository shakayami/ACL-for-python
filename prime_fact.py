from math import gcd
import random
from collections import Counter


def is_probable_prime(n):
    if n == 2:
        return True
    if n == 1 or n & 1 == 0:
        return False
    d = (n - 1) >> 1
    while d & 1 == 0:
        d >>= 1

    for k in range(100):
        a = random.randint(1, n - 1)
        t = d
        y = pow(a, t, n)
        while t != n - 1 and y != 1 and y != n - 1:
            y = (y * y) % n
            t <<= 1
        if y != n - 1 and t & 1 == 0:
            return False
    return True


def _solve(N):
    if is_probable_prime(N):
        return N
    while True:
        x = random.randrange(N)
        c = random.randrange(N)
        y = (x * x + c) % N
        d = 1
        while d == 1:
            d = gcd(x - y, N)
            x = (x * x + c) % N
            y = (y * y + c) % N
            y = (y * y + c) % N
        if 1 < d < N:
            return _solve(d)


def prime_fact(N):
    res = Counter()
    p = 2
    while p <= 10**4 and N > 1:
        if N % p == 0:
            while N % p == 0:
                res[p] += 1
                N //= p
        p += 1
    while N > 1:
        p = _solve(N)
        while (N % p) == 0:
            res[p] += 1
            N //= p
    return res


def divisors(N):
    PF = prime_fact(N)
    res = [1]
    for p, e in PF.items():
        for i in range(len(res) * e):
            res.append(res[i] * p)
    return res


def totient(N):
    PF = prime_fact(N)
    res = N
    for p in PF:
        res -= res // p
    return res


def lcm(x, y):
    return (x * y) // gcd(x, y)
