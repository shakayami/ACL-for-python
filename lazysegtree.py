class lazy_segtree:
    def update(self, k):
        self.d[k] = self.op(self.d[2 * k], self.d[2 * k + 1])

    def all_apply(self, k, f):
        self.d[k] = self.mapping(f, self.d[k])
        if k < self.size:
            self.lz[k] = self.composition(f, self.lz[k])

    def push(self, k):
        self.all_apply(2 * k, self.lz[k])
        self.all_apply(2 * k + 1, self.lz[k])
        self.lz[k] = self.identity

    def __init__(self, V, OP, E, MAPPING, COMPOSITION, ID):
        self.n = len(V)
        self.log = (self.n - 1).bit_length()
        self.size = 1 << self.log
        self.d = [E for i in range(2 * self.size)]
        self.lz = [ID for i in range(self.size)]
        self.e = E
        self.op = OP
        self.mapping = MAPPING
        self.composition = COMPOSITION
        self.identity = ID
        d = self.d
        for i in range(self.n):
            d[self.size + i] = V[i]
        op = self.op
        for i in range(self.size - 1, 0, -1):
            d[i] = op(d[2 * i], d[2 * i + 1])

    def set(self, p, x):
        assert 0 <= p and p < self.n
        d = self.d
        lz = self.lz
        mapping = self.mapping
        composition = self.composition
        identity = self.identity
        op = self.op
        size = self.size
        p += size
        for i in range(self.log, 0, -1):
            k = p >> i
            k2 = 2 * k
            pf = lz[k]
            d[k2] = mapping(pf, d[k2])
            if k2 < size:
                lz[k2] = composition(pf, lz[k2])
            k2 += 1
            d[k2] = mapping(pf, d[k2])
            if k2 < size:
                lz[k2] = composition(pf, lz[k2])
            lz[k] = identity
        d[p] = x
        for i in range(1, self.log + 1):
            k = p >> i
            d[k] = op(d[2 * k], d[2 * k + 1])

    def get(self, p):
        assert 0 <= p and p < self.n
        d = self.d
        lz = self.lz
        mapping = self.mapping
        composition = self.composition
        identity = self.identity
        size = self.size
        p += size
        for i in range(self.log, 0, -1):
            k = p >> i
            k2 = 2 * k
            pf = lz[k]
            d[k2] = mapping(pf, d[k2])
            if k2 < size:
                lz[k2] = composition(pf, lz[k2])
            k2 += 1
            d[k2] = mapping(pf, d[k2])
            if k2 < size:
                lz[k2] = composition(pf, lz[k2])
            lz[k] = identity
        return d[p]

    def prod(self, l, r):
        assert 0 <= l and l <= r and r <= self.n
        if l == r:
            return self.e
        d = self.d
        lz = self.lz
        mapping = self.mapping
        composition = self.composition
        identity = self.identity
        op = self.op
        size = self.size
        log = self.log
        l += size
        r += size
        for i in range(log, 0, -1):
            if ((l >> i) << i) != l:
                k = l >> i
                k2 = 2 * k
                pf = lz[k]
                d[k2] = mapping(pf, d[k2])
                if k2 < size:
                    lz[k2] = composition(pf, lz[k2])
                k2 += 1
                d[k2] = mapping(pf, d[k2])
                if k2 < size:
                    lz[k2] = composition(pf, lz[k2])
                lz[k] = identity
            if ((r >> i) << i) != r:
                k = r >> i
                k2 = 2 * k
                pf = lz[k]
                d[k2] = mapping(pf, d[k2])
                if k2 < size:
                    lz[k2] = composition(pf, lz[k2])
                k2 += 1
                d[k2] = mapping(pf, d[k2])
                if k2 < size:
                    lz[k2] = composition(pf, lz[k2])
                lz[k] = identity
        sml, smr = self.e, self.e
        while l < r:
            if l & 1:
                sml = op(sml, d[l])
                l += 1
            if r & 1:
                r -= 1
                smr = op(d[r], smr)
            l >>= 1
            r >>= 1
        return op(sml, smr)

    def all_prod(self):
        return self.d[1]

    def apply_point(self, p, f):
        assert 0 <= p and p < self.n
        d = self.d
        lz = self.lz
        mapping = self.mapping
        composition = self.composition
        identity = self.identity
        op = self.op
        size = self.size
        p += size
        for i in range(self.log, 0, -1):
            k = p >> i
            k2 = 2 * k
            pf = lz[k]
            d[k2] = mapping(pf, d[k2])
            if k2 < size:
                lz[k2] = composition(pf, lz[k2])
            k2 += 1
            d[k2] = mapping(pf, d[k2])
            if k2 < size:
                lz[k2] = composition(pf, lz[k2])
            lz[k] = identity
        d[p] = mapping(f, d[p])
        for i in range(1, self.log + 1):
            k = p >> i
            d[k] = op(d[2 * k], d[2 * k + 1])

    def apply(self, l, r, f):
        assert 0 <= l and l <= r and r <= self.n
        if l == r:
            return
        d = self.d
        lz = self.lz
        mapping = self.mapping
        composition = self.composition
        identity = self.identity
        op = self.op
        size = self.size
        log = self.log
        l += size
        r += size
        for i in range(log, 0, -1):
            if ((l >> i) << i) != l:
                k = l >> i
                k2 = 2 * k
                pf = lz[k]
                d[k2] = mapping(pf, d[k2])
                if k2 < size:
                    lz[k2] = composition(pf, lz[k2])
                k2 += 1
                d[k2] = mapping(pf, d[k2])
                if k2 < size:
                    lz[k2] = composition(pf, lz[k2])
                lz[k] = identity
            if ((r >> i) << i) != r:
                k = (r - 1) >> i
                k2 = 2 * k
                pf = lz[k]
                d[k2] = mapping(pf, d[k2])
                if k2 < size:
                    lz[k2] = composition(pf, lz[k2])
                k2 += 1
                d[k2] = mapping(pf, d[k2])
                if k2 < size:
                    lz[k2] = composition(pf, lz[k2])
                lz[k] = identity
        l2, r2 = l, r
        while l < r:
            if l & 1:
                d[l] = mapping(f, d[l])
                if l < size:
                    lz[l] = composition(f, lz[l])
                l += 1
            if r & 1:
                r -= 1
                d[r] = mapping(f, d[r])
                if r < size:
                    lz[r] = composition(f, lz[r])
            l >>= 1
            r >>= 1
        l, r = l2, r2
        for i in range(1, log + 1):
            if ((l >> i) << i) != l:
                k = l >> i
                d[k] = op(d[2 * k], d[2 * k + 1])
            if ((r >> i) << i) != r:
                k = (r - 1) >> i
                d[k] = op(d[2 * k], d[2 * k + 1])

    def max_right(self, l, g):
        assert 0 <= l and l <= self.n
        assert g(self.e)
        if l == self.n:
            return self.n
        d = self.d
        lz = self.lz
        mapping = self.mapping
        composition = self.composition
        identity = self.identity
        op = self.op
        size = self.size
        l += size
        for i in range(self.log, 0, -1):
            k = l >> i
            k2 = 2 * k
            pf = lz[k]
            d[k2] = mapping(pf, d[k2])
            if k2 < size:
                lz[k2] = composition(pf, lz[k2])
            k2 += 1
            d[k2] = mapping(pf, d[k2])
            if k2 < size:
                lz[k2] = composition(pf, lz[k2])
            lz[k] = identity
        sm = self.e
        while 1:
            while l % 2 == 0:
                l >>= 1
            if not (g(op(sm, d[l]))):
                while l < size:
                    k = l
                    k2 = 2 * k
                    pf = lz[k]
                    d[k2] = mapping(pf, d[k2])
                    if k2 < size:
                        lz[k2] = composition(pf, lz[k2])
                    k2 += 1
                    d[k2] = mapping(pf, d[k2])
                    if k2 < size:
                        lz[k2] = composition(pf, lz[k2])
                    lz[k] = identity
                    l = 2 * l
                    if g(op(sm, d[l])):
                        sm = op(sm, d[l])
                        l += 1
                return l - size
            sm = op(sm, d[l])
            l += 1
            if (l & -l) == l:
                break
        return self.n

    def min_left(self, r, g):
        assert 0 <= r and r <= self.n
        assert g(self.e)
        if r == 0:
            return 0
        d = self.d
        lz = self.lz
        mapping = self.mapping
        composition = self.composition
        identity = self.identity
        op = self.op
        size = self.size
        r += size
        for i in range(self.log, 0, -1):
            k = (r - 1) >> i
            k2 = 2 * k
            pf = lz[k]
            d[k2] = mapping(pf, d[k2])
            if k2 < size:
                lz[k2] = composition(pf, lz[k2])
            k2 += 1
            d[k2] = mapping(pf, d[k2])
            if k2 < size:
                lz[k2] = composition(pf, lz[k2])
            lz[k] = identity
        sm = self.e
        while 1:
            r -= 1
            while r > 1 and (r % 2):
                r >>= 1
            if not (g(op(d[r], sm))):
                while r < size:
                    k = r
                    k2 = 2 * k
                    pf = lz[k]
                    d[k2] = mapping(pf, d[k2])
                    if k2 < size:
                        lz[k2] = composition(pf, lz[k2])
                    k2 += 1
                    d[k2] = mapping(pf, d[k2])
                    if k2 < size:
                        lz[k2] = composition(pf, lz[k2])
                    lz[k] = identity
                    r = 2 * r + 1
                    if g(op(d[r], sm)):
                        sm = op(d[r], sm)
                        r -= 1
                return r + 1 - size
            sm = op(d[r], sm)
            if (r & -r) == r:
                break
        return 0
