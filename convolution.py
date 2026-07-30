import struct


class FFT:
    def primitive_root_constexpr(self, m):
        if m == 2:
            return 1
        if m == 167772161:
            return 3
        if m == 469762049:
            return 3
        if m == 754974721:
            return 11
        if m == 998244353:
            return 3
        divs = [0] * 20
        divs[0] = 2
        cnt = 1
        x = (m - 1) // 2
        while x % 2 == 0:
            x //= 2
        i = 3
        while i * i <= x:
            if x % i == 0:
                divs[cnt] = i
                cnt += 1
                while x % i == 0:
                    x //= i
            i += 2
        if x > 1:
            divs[cnt] = x
            cnt += 1
        g = 2
        while 1:
            ok = True
            for i in range(cnt):
                if pow(g, (m - 1) // divs[i], m) == 1:
                    ok = False
                    break
            if ok:
                return g
            g += 1

    def bsf(self, x):
        res = 0
        while x % 2 == 0:
            res += 1
            x //= 2
        return res

    rank2 = 0
    root = []
    iroot = []
    rate2 = []
    irate2 = []
    rate3 = []
    irate3 = []

    def __init__(self, MOD):
        self.mod = MOD
        self.g = self.primitive_root_constexpr(self.mod)
        self.rank2 = self.bsf(self.mod - 1)
        self.root = [0 for i in range(self.rank2 + 1)]
        self.iroot = [0 for i in range(self.rank2 + 1)]
        self.rate2 = [0 for i in range(self.rank2)]
        self.irate2 = [0 for i in range(self.rank2)]
        self.rate3 = [0 for i in range(self.rank2 - 1)]
        self.irate3 = [0 for i in range(self.rank2 - 1)]
        self.root[self.rank2] = pow(self.g, (self.mod - 1) >> self.rank2, self.mod)
        self.iroot[self.rank2] = pow(self.root[self.rank2], self.mod - 2, self.mod)
        for i in range(self.rank2 - 1, -1, -1):
            self.root[i] = (self.root[i + 1] ** 2) % self.mod
            self.iroot[i] = (self.iroot[i + 1] ** 2) % self.mod
        prod = 1
        iprod = 1
        for i in range(self.rank2 - 1):
            self.rate2[i] = (self.root[i + 2] * prod) % self.mod
            self.irate2[i] = (self.iroot[i + 2] * iprod) % self.mod
            prod = (prod * self.iroot[i + 2]) % self.mod
            iprod = (iprod * self.root[i + 2]) % self.mod
        prod = 1
        iprod = 1
        for i in range(self.rank2 - 2):
            self.rate3[i] = (self.root[i + 3] * prod) % self.mod
            self.irate3[i] = (self.iroot[i + 3] * iprod) % self.mod
            prod = (prod * self.iroot[i + 3]) % self.mod
            iprod = (iprod * self.root[i + 3]) % self.mod

    def butterfly(self, a):
        n = len(a)
        h = (n - 1).bit_length()
        # Hoisting the instance attributes into locals removes an attribute
        # lookup per use from the innermost loops, which dominate the runtime.
        mod = self.mod
        rate2 = self.rate2
        rate3 = self.rate3
        imag = self.root[2]

        LEN = 0
        while LEN < h:
            if h - LEN == 1:
                p = 1 << (h - LEN - 1)
                rot = 1
                for s in range(1 << LEN):
                    offset = s << (h - LEN)
                    end = offset + p
                    if rot == 1:
                        for i in range(offset, end):
                            j = i + p
                            l = a[i]
                            r = a[j]
                            a[i] = (l + r) % mod
                            a[j] = (l - r) % mod
                    else:
                        for i in range(offset, end):
                            j = i + p
                            l = a[i]
                            r = a[j] * rot
                            a[i] = (l + r) % mod
                            a[j] = (l - r) % mod
                    rot = rot * rate2[(~s & -~s).bit_length() - 1] % mod
                LEN += 1
            else:
                p = 1 << (h - LEN - 2)
                p2 = p + p
                p3 = p2 + p
                rot = 1
                for s in range(1 << LEN):
                    offset = s << (h - LEN)
                    end = offset + p
                    if rot == 1:
                        for i in range(offset, end):
                            i1 = i + p
                            i2 = i + p2
                            i3 = i + p3
                            a0 = a[i]
                            a1 = a[i1]
                            a2 = a[i2]
                            a3 = a[i3]
                            a02 = a0 + a2
                            a13 = a1 + a3
                            a0n2 = a0 - a2
                            a1na3imag = (a1 - a3) % mod * imag
                            a[i] = (a02 + a13) % mod
                            a[i1] = (a02 - a13) % mod
                            a[i2] = (a0n2 + a1na3imag) % mod
                            a[i3] = (a0n2 - a1na3imag) % mod
                    else:
                        rot2 = rot * rot % mod
                        rot3 = rot2 * rot % mod
                        for i in range(offset, end):
                            i1 = i + p
                            i2 = i + p2
                            i3 = i + p3
                            a0 = a[i]
                            a1 = a[i1] * rot
                            a2 = a[i2] * rot2
                            a3 = a[i3] * rot3
                            a02 = a0 + a2
                            a13 = a1 + a3
                            a0n2 = a0 - a2
                            a1na3imag = (a1 - a3) % mod * imag
                            a[i] = (a02 + a13) % mod
                            a[i1] = (a02 - a13) % mod
                            a[i2] = (a0n2 + a1na3imag) % mod
                            a[i3] = (a0n2 - a1na3imag) % mod
                    rot = rot * rate3[(~s & -~s).bit_length() - 1] % mod
                LEN += 2

    def butterfly_inv(self, a):
        n = len(a)
        h = (n - 1).bit_length()
        mod = self.mod
        irate2 = self.irate2
        irate3 = self.irate3
        iimag = self.iroot[2]

        LEN = h
        while LEN:
            if LEN == 1:
                p = 1 << (h - LEN)
                irot = 1
                for s in range(1 << (LEN - 1)):
                    offset = s << (h - LEN + 1)
                    end = offset + p
                    if irot == 1:
                        for i in range(offset, end):
                            j = i + p
                            l = a[i]
                            r = a[j]
                            a[i] = (l + r) % mod
                            a[j] = (l - r) % mod
                    else:
                        for i in range(offset, end):
                            j = i + p
                            l = a[i]
                            r = a[j]
                            a[i] = (l + r) % mod
                            a[j] = (l - r) * irot % mod
                    irot = irot * irate2[(~s & -~s).bit_length() - 1] % mod
                LEN -= 1
            else:
                p = 1 << (h - LEN)
                p2 = p + p
                p3 = p2 + p
                irot = 1
                for s in range(1 << (LEN - 2)):
                    offset = s << (h - LEN + 2)
                    end = offset + p
                    if irot == 1:
                        for i in range(offset, end):
                            i1 = i + p
                            i2 = i + p2
                            i3 = i + p3
                            a0 = a[i]
                            a1 = a[i1]
                            a2 = a[i2]
                            a3 = a[i3]
                            a01 = a0 + a1
                            a23 = a2 + a3
                            a0n1 = a0 - a1
                            a2na3iimag = (a2 - a3) * iimag % mod
                            a[i] = (a01 + a23) % mod
                            a[i1] = (a0n1 + a2na3iimag) % mod
                            a[i2] = (a01 - a23) % mod
                            a[i3] = (a0n1 - a2na3iimag) % mod
                    else:
                        irot2 = irot * irot % mod
                        irot3 = irot * irot2 % mod
                        for i in range(offset, end):
                            i1 = i + p
                            i2 = i + p2
                            i3 = i + p3
                            a0 = a[i]
                            a1 = a[i1]
                            a2 = a[i2]
                            a3 = a[i3]
                            a01 = a0 + a1
                            a23 = a2 + a3
                            a0n1 = a0 - a1
                            a2na3iimag = (a2 - a3) * iimag % mod
                            a[i] = (a01 + a23) % mod
                            a[i1] = (a0n1 + a2na3iimag) * irot % mod
                            a[i2] = (a01 - a23) * irot2 % mod
                            a[i3] = (a0n1 - a2na3iimag) * irot3 % mod
                    irot = irot * irate3[(~s & -~s).bit_length() - 1] % mod
                LEN -= 2

    # struct codes for the fixed-width integers usable as packing slots
    _code = {1: "B", 2: "H", 4: "I", 8: "Q"}
    # slot widths (in bytes) that struct can pack/unpack with at most two fields
    _widths = (1, 2, 4, 8, 9, 10, 12, 16)
    _packers = {}
    _CHUNK = 256

    def _pack(self, a, nb, w):
        """Encode a as sum(a[i] << (8 * nb * i)), one nb-byte slot per element.

        w is the struct field width in bytes (None to fall back to to_bytes).
        """
        if w is None:
            return int.from_bytes(
                b"".join(x.to_bytes(nb, "little") for x in a), "little"
            )
        entry = self._packers.get((nb, w))
        if entry is None:
            unit = self._code[w] + ("%dx" % (nb - w) if nb > w else "")
            entry = (struct.Struct("<" + unit * self._CHUNK).pack, unit)
            self._packers[(nb, w)] = entry
        pack_chunk, unit = entry
        n = len(a)
        chunk = self._CHUNK
        if n <= chunk:
            return int.from_bytes(struct.pack("<" + unit * n, *a), "little")
        tail = n % chunk
        end = n - tail
        parts = [pack_chunk(*a[i : i + chunk]) for i in range(0, end, chunk)]
        if tail:
            parts.append(struct.pack("<" + unit * tail, *a[end:]))
        return int.from_bytes(b"".join(parts), "little")

    def _unpack(self, buf, nb, length, mod):
        """Inverse of _pack: read length slots of nb bytes, reduced mod mod."""
        code = self._code.get(nb) if nb <= 8 else self._code.get(nb - 8)
        if code is not None:
            if nb <= 8:
                res = [x % mod for (x,) in struct.iter_unpack("<" + code, buf)]
            else:
                res = [
                    (lo | hi << 64) % mod
                    for lo, hi in struct.iter_unpack("<Q" + code, buf)
                ]
            del res[length:]
            return res
        frm = int.from_bytes
        return [frm(buf[i : i + nb], "little") % mod for i in range(0, nb * length, nb)]

    def _convolution_int(self, a, b, amax, bmax):
        """Kronecker substitution: multiply the two operands as one big int.

        Each coefficient gets its own zero-padded slot, wide enough that no
        coefficient of the product can carry into the next slot, so CPython's
        (C-level, Karatsuba) integer multiply does the whole convolution.
        """
        n = len(a)
        m = len(b)
        mod = self.mod
        vb = max((amax.bit_length() + 7) >> 3, (bmax.bit_length() + 7) >> 3, 1)
        nb = max(((min(n, m) * amax * bmax).bit_length() + 7) >> 3, vb)
        w = None
        if nb <= 16 and vb <= 8:
            for width in self._widths:
                if width >= nb:
                    nb = width
                    break
            w = 1
            while w < vb:
                w <<= 1
        prod = self._pack(a, nb, w) * self._pack(b, nb, w)
        return self._unpack(prod.to_bytes(nb * (n + m), "little"), nb, n + m - 1, mod)

    def convolution(self, a, b):
        n = len(a)
        m = len(b)
        if not (a) or not (b):
            return []
        mod = self.mod
        if n * m <= 40:
            res = [0] * (n + m - 1)
            for i, ai in enumerate(a):
                if ai:
                    ai %= mod
                    for j, bj in enumerate(b, i):
                        res[j] = (res[j] + ai * bj) % mod
            return res
        # Both remaining paths want representatives in [0, mod).
        amax = max(a)
        if min(a) < 0 or amax >= mod:
            a = [x % mod for x in a]
            amax = max(a)
        bmax = max(b)
        if min(b) < 0 or bmax >= mod:
            b = [x % mod for x in b]
            bmax = max(b)
        z = 1 << ((n + m - 2).bit_length())
        # Cost model, fitted on CPython 3.11.  Kronecker substitution costs
        # about 8e-10 * (hi / lo) * (lo * nb) ** 1.585 seconds (Karatsuba on
        # lo * nb bytes, repeated hi / lo times for a lopsided product), while
        # the NTT costs about 2.7e-7 * z * log2(z).  Their ratio gives the
        # constant below.  The NTT only wins once both operands are large:
        # small, lopsided or small-coefficient inputs stay on the integer path.
        lo, hi = (n, m) if n < m else (m, n)
        nb = max(((lo * amax * bmax).bit_length() + 7) >> 3, 1)
        if hi * (lo * nb) ** 1.585 < 337.0 * lo * z * (z.bit_length() - 1):
            return self._convolution_int(a, b, amax, bmax)
        # butterfly_inv is unnormalized, so the result needs scaling by 1/z.
        # Folding that into b before its transform costs m multiplications
        # instead of a separate pass (and an extra list) over the z outputs.
        iz = pow(z, mod - 2, mod)
        a = a + [0] * (z - n)
        b = [x * iz % mod for x in b] + [0] * (z - m)
        self.butterfly(a)
        self.butterfly(b)
        c = [x * y % mod for x, y in zip(a, b)]
        self.butterfly_inv(c)
        del c[n + m - 1 :]
        return c
