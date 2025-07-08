#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mincostflow


class TestMinCostFlow(unittest.TestCase):
    """Test cases for mincostflow module"""

    def practice2_e(self, n, k, A, ans):
        BIG = 10**9
        g = mincostflow.mcf_graph(2 * n + 2)
        s = 2 * n
        t = 2 * n + 1
        g.add_edge(s, t, n * k, BIG)
        for i in range(n):
            g.add_edge(s, i, k, 0)
            g.add_edge(n + i, t, k, 0)
        for i in range(n):
            for j in range(n):
                g.add_edge(i, n + j, 1, BIG - A[i][j])
        result = g.flow(s, t, n * k)
        res = n * k * BIG - result[1]
        self.assertEqual(res, ans)

    def test_practice2_e_1(self):
        self.practice2_e(3, 1, [[5, 3, 2], [1, 4, 8], [7, 6, 9]], 19)

    def test_practice_e_2(self):
        self.practice2_e(3, 2, [[10, 10, 1], [10, 10, 1], [1, 1, 10]], 50)

    def test_placeholder(self):
        """Placeholder test - add your test cases here"""
        pass


if __name__ == "__main__":
    unittest.main()
