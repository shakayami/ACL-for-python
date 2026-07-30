class segtree:
    n = 1
    size = 1
    log = 2
    d = [0]
    op = None
    e = 10**15

    def __init__(self, V, OP, E):
        self.n = len(V)
        self.op = OP
        self.e = E
        self.log = (self.n - 1).bit_length()
        self.size = 1 << self.log
        self.d = [E for i in range(2 * self.size)]
        d = self.d
        for i in range(self.n):
            d[self.size + i] = V[i]
        op = self.op
        for i in range(self.size - 1, 0, -1):
            d[i] = op(d[2 * i], d[2 * i + 1])

    def set(self, p, x):
        assert 0 <= p and p < self.n
        d = self.d
        op = self.op
        p += self.size
        d[p] = x
        for i in range(1, self.log + 1):
            k = p >> i
            d[k] = op(d[2 * k], d[2 * k + 1])

    def get(self, p):
        assert 0 <= p and p < self.n
        return self.d[p + self.size]

    def prod(self, l, r):
        assert 0 <= l and l <= r and r <= self.n
        d = self.d
        op = self.op
        sml = self.e
        smr = self.e
        l += self.size
        r += self.size
        while l < r:
            if l & 1:
                sml = op(sml, d[l])
                l += 1
            if r & 1:
                smr = op(d[r - 1], smr)
                r -= 1
            l >>= 1
            r >>= 1
        return op(sml, smr)

    def all_prod(self):
        return self.d[1]

    def max_right(self, l, f):
        assert 0 <= l and l <= self.n
        assert f(self.e)
        if l == self.n:
            return self.n
        d = self.d
        op = self.op
        size = self.size
        l += size
        sm = self.e
        while 1:
            while l % 2 == 0:
                l >>= 1
            if not (f(op(sm, d[l]))):
                while l < size:
                    l = 2 * l
                    if f(op(sm, d[l])):
                        sm = op(sm, d[l])
                        l += 1
                return l - size
            sm = op(sm, d[l])
            l += 1
            if (l & -l) == l:
                break
        return self.n

    def min_left(self, r, f):
        assert 0 <= r and r <= self.n
        assert f(self.e)
        if r == 0:
            return 0
        d = self.d
        op = self.op
        size = self.size
        r += size
        sm = self.e
        while 1:
            r -= 1
            while r > 1 and (r % 2):
                r >>= 1
            if not (f(op(d[r], sm))):
                while r < size:
                    r = 2 * r + 1
                    if f(op(d[r], sm)):
                        sm = op(d[r], sm)
                        r -= 1
                return r + 1 - size
            sm = op(d[r], sm)
            if (r & -r) == r:
                break
        return 0

    def update(self, k):
        self.d[k] = self.op(self.d[2 * k], self.d[2 * k + 1])

    def __str__(self):
        return str([self.get(i) for i in range(self.n)])
