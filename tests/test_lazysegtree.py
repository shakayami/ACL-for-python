#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lazysegtree


class TestLazySegTree(unittest.TestCase):
    """Test cases for lazysegtree module"""

    def practice2_k(self, N, Q, A, query, ans):
        """Practice problem 2-K implementation"""
        res = []
        mod = 998244353

        def operate(a, b):
            return ((a[0] + b[0]) % mod, a[1] + b[1])

        def mapping(f, x):
            return ((f[0] * x[0] + x[1] * f[1]) % mod, x[1])

        def composition(f, g):
            return ((f[0] * g[0]) % mod, (g[1] * f[0] + f[1]) % mod)

        seg = lazysegtree.lazy_segtree(
            [(i, 1) for i in A], operate, (0, 0), mapping, composition, (1, 0)
        )
        for i in range(Q):
            seq = query[i]
            if seq[0] == 0:
                dummy, l, r, b, c = seq
                seg.apply(l, r, (b, c))
            else:
                dummy, l, r = seq
                res.append(seg.prod(l, r)[0])
        self.assertEqual(res, ans)

    def test_practice2_k(self):
        """Test practice problem 2-K"""
        self.practice2_k(
            5,
            7,
            [1, 2, 3, 4, 5],
            [
                (1, 0, 5),
                (0, 2, 4, 100, 101),
                (1, 0, 3),
                (0, 1, 3, 102, 103),
                (1, 2, 5),
                (0, 2, 5, 104, 105),
                (1, 0, 5),
            ],
            [15, 404, 41511, 4317767],
        )

    def practice2_l(self, N, Q, A, query, ans):
        a = [(0, 1, 0) if _ == 0 else (0, 0, 1) for _ in A]

        def op(x, y):
            return (x[0] + y[0] + x[2] * y[1], x[1] + y[1], x[2] + y[2])

        def mapping(f, x):
            if f == 0:
                return x
            else:
                return (x[1] * x[2] - x[0], x[2], x[1])

        def composition(f, g):
            return f ^ g

        seg = lazysegtree.lazy_segtree(a, op, (0, 0, 0), mapping, composition, 0)
        res = []
        for i in range(Q):
            t, l, r = query[i]
            l -= 1
            if t == 1:
                seg.apply(l, r, 1)
            else:
                tmp = seg.prod(l, r)
                res.append(tmp[0])
        self.assertEqual(res, ans)

    def test_practice2_l(self):
        self.practice2_l(
            5,
            5,
            [0, 1, 0, 0, 1],
            [(2, 1, 5), (1, 3, 4), (2, 2, 5), (1, 1, 3), (2, 1, 2)],
            [2, 0, 1],
        )


if __name__ == "__main__":
    unittest.main()
