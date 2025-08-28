import math
import random
import collections.Counter

def is_probable_prime(n):
    if n < 2:
        return False
    SMALL_PRIME = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in SMALL_PRIME:
        if n == p:
            return True
        if n % p == 0:
            return False

    r = math.isqrt(n)
    if r * r == n:
        return False

    d = n - 1
    s = (d & -d).bit_length() - 1
    d >>= s

    for a in SMALL_PRIME:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
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
            d = math.gcd(x - y, N)
            x = (x * x + c) % N
            y = (y * y + c) % N
            y = (y * y + c) % N
        if 1 < d < N:
            return _solve(d)


def prime_fact(N):
    res = collections.Counter()
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
    return (x * y) // math.gcd(x, y)
