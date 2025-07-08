#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import segtree


class TestSegTree(unittest.TestCase):
    """Test cases for segtree module"""

    def practice2_j(self, N, Q, A, query, ans):
        G = segtree.segtree([i for i in A], max, -1)
        res = []
        for i in range(Q):
            t, a, b = query[i]
            if t == 1:
                x, v = a, b
                x -= 1
                G.set(x, v)
            if t == 2:
                l, r = a, b
                l -= 1
                r -= 1
                res.append(G.prod(l, r + 1))
            if t == 3:
                x, v = a, b
                x -= 1

                def f(t):
                    if v > t:
                        return True
                    else:
                        return False

                res.append(G.max_right(x, f) + 1)
        self.assertEqual(res, ans)

    def test_practice2_j(self):
        self.practice2_j(
            5,
            5,
            [1, 2, 3, 2, 1],
            [(2, 1, 5), (3, 2, 3), (1, 3, 1), (2, 2, 4), (3, 1, 3)],
            [3, 3, 2, 6],
        )


if __name__ == "__main__":
    unittest.main()
