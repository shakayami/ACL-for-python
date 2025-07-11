#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dsu


class TestDSU(unittest.TestCase):
    """Test cases for dsu module"""

    def test_dsu_basic(self):
        """Test basic DSU operations"""
        d = dsu.dsu(5)
        d.merge(0, 1)
        d.merge(2, 3)
        self.assertTrue(d.same(0, 1))
        self.assertFalse(d.same(0, 2))
        self.assertEqual(d.size(0), 2)
        self.assertEqual(d.size(2), 2)

    def practice2_a(self, N, Q, query, ans):
        G = dsu.dsu(N)
        res = []
        for t, u, v in query:
            if t == 0:
                G.merge(u, v)
            else:
                res.append(1 if G.same(u, v) else 0)
        self.assertEqual(ans, res)

    def test_practice2_a(self):
        self.practice2_a(
            4,
            7,
            [
                (1, 0, 1),
                (0, 0, 1),
                (0, 2, 3),
                (1, 0, 1),
                (1, 1, 2),
                (0, 0, 2),
                (1, 1, 3),
            ],
            [0, 1, 0, 1],
        )


if __name__ == "__main__":
    unittest.main()
