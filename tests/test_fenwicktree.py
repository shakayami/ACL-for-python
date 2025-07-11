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

    def test_single_element(self):
        """Test Fenwick Tree with single element"""
        ft = fenwicktree.fenwick_tree(1)
        ft.add(0, 5)
        self.assertEqual(ft.sum(0, 1), 5)

    def test_empty_range(self):
        """Test empty range sum"""
        ft = fenwicktree.fenwick_tree(5)
        ft.add(0, 1)
        ft.add(1, 2)
        self.assertEqual(ft.sum(2, 2), 0)
        self.assertEqual(ft.sum(0, 0), 0)

    def test_negative_values(self):
        """Test Fenwick Tree with negative values"""
        ft = fenwicktree.fenwick_tree(5)
        ft.add(0, 5)
        ft.add(1, -3)
        ft.add(2, 7)
        ft.add(3, -2)

        self.assertEqual(ft.sum(0, 2), 2)  # 5 + (-3) = 2
        self.assertEqual(ft.sum(1, 4), 2)  # -3 + 7 + (-2) = 2
        self.assertEqual(ft.sum(0, 4), 7)  # 5 + (-3) + 7 + (-2) = 7

    def test_multiple_additions(self):
        """Test multiple additions to same index"""
        ft = fenwicktree.fenwick_tree(3)
        ft.add(0, 1)
        ft.add(0, 2)
        ft.add(0, 3)
        self.assertEqual(ft.sum(0, 1), 6)

        ft.add(1, 5)
        ft.add(1, -2)
        self.assertEqual(ft.sum(0, 2), 9)  # 6 + 3 = 9

    def test_range_sums(self):
        """Test various range sum queries"""
        ft = fenwicktree.fenwick_tree(6)
        values = [1, 3, 5, 7, 9, 11]
        for i, val in enumerate(values):
            ft.add(i, val)

        # Test prefix sums
        self.assertEqual(ft.sum(0, 1), 1)
        self.assertEqual(ft.sum(0, 2), 4)
        self.assertEqual(ft.sum(0, 3), 9)
        self.assertEqual(ft.sum(0, 6), 36)

        # Test range sums
        self.assertEqual(ft.sum(1, 3), 8)  # 3 + 5 = 8
        self.assertEqual(ft.sum(2, 5), 21)  # 5 + 7 + 9 = 21
        self.assertEqual(ft.sum(3, 6), 27)  # 7 + 9 + 11 = 27

    def test_large_fenwick_tree(self):
        """Test Fenwick Tree with larger size"""
        n = 1000
        ft = fenwicktree.fenwick_tree(n)

        # Add values 1, 2, 3, ..., n
        for i in range(n):
            ft.add(i, i + 1)

        # Test some range sums
        self.assertEqual(ft.sum(0, 10), 55)  # sum of 1..10
        self.assertEqual(ft.sum(0, 100), 5050)  # sum of 1..100
        self.assertEqual(ft.sum(50, 100), 3775)  # sum of 51..100

    def test_zero_initialization(self):
        """Test that Fenwick Tree starts with all zeros"""
        ft = fenwicktree.fenwick_tree(5)
        for i in range(6):
            self.assertEqual(ft.sum(0, i), 0)

    def test_boundary_conditions(self):
        """Test boundary conditions"""
        ft = fenwicktree.fenwick_tree(5)
        ft.add(0, 1)
        ft.add(4, 5)

        self.assertEqual(ft.sum(0, 1), 1)
        self.assertEqual(ft.sum(4, 5), 5)
        self.assertEqual(ft.sum(0, 5), 6)
        self.assertEqual(ft.sum(1, 4), 0)


if __name__ == "__main__":
    unittest.main()
