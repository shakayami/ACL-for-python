#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fenwicktree


class TestFenwickTree(unittest.TestCase):
    """Test cases for fenwicktree module"""

    def practice2_b(self, N, Q, a, query, ans):
        FT = fenwicktree.fenwick_tree(N)
        for i in range(N):
            FT.add(i, a[i])
        res = []
        for t, a, b in query:
            if t == 0:
                FT.add(a, b)
            else:
                res.append(FT.sum(a, b))
        self.assertEqual(res, ans)

    def test_sample(self):
        """Placeholder test - add your test cases here"""
        self.practice2_b(
            5,
            5,
            [1, 2, 3, 4, 5],
            [(1, 0, 5), (1, 2, 4), (0, 3, 10), (1, 0, 5), (1, 0, 3)],
            [15, 7, 25, 6],
        )

    def test_fenwick_basic(self):
        """Test basic Fenwick Tree operations"""
        import fenwicktree

        ft = fenwicktree.fenwick_tree(5)
        ft.add(0, 1)
        ft.add(1, 2)
        ft.add(2, 3)
        self.assertEqual(ft.sum(0, 3), 6)
        self.assertEqual(ft.sum(1, 3), 5)


if __name__ == "__main__":
    unittest.main()
