#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import acl_math


class TestACLMath(unittest.TestCase):
    """Test cases for acl_math module"""

    def test_floorsum(self):
        query = [
            (4, 10, 6, 3, 3),
            (6, 5, 4, 3, 13),
            (1, 1, 0, 0, 0),
            (31415, 92653, 58979, 32384, 314095480),
            (1000000000, 1000000000, 999999999, 999999999, 499999999500000000),
        ]
        for n, m, a, b, ans in query:
            self.assertEqual(acl_math.floor_sum(n, m, a, b), ans)

    def test_crt(self):
        A = 37
        B = 56
        C = 15
        S = set(range(A * B * C))
        for a in range(A):
            for b in range(B):
                for c in range(C):
                    x, X = acl_math.crt((a, b, c), (A, B, C))
                    self.assertEqual(X, A * B * C)
                    self.assertTrue(x in S)
                    S.discard(x)

    def test_inv_gcd_basic(self):
        """Test basic inv_gcd functionality"""
        # gcd(3, 7) = 1, 3 * 5 ≡ 1 (mod 7)
        g, x = acl_math.inv_gcd(3, 7)
        self.assertEqual(g, 1)
        self.assertEqual((3 * x) % 7, 1)

        # gcd(6, 9) = 3
        g, x = acl_math.inv_gcd(6, 9)
        self.assertEqual(g, 3)

    def test_inv_mod_basic(self):
        """Test basic modular inverse"""
        # 3 * 5 ≡ 1 (mod 7)
        self.assertEqual(acl_math.inv_mod(3, 7), 5)

        # 2 * 4 ≡ 1 (mod 7)
        self.assertEqual(acl_math.inv_mod(2, 7), 4)

        # Test with larger numbers
        inv = acl_math.inv_mod(123, 997)  # 997 is prime
        self.assertEqual((123 * inv) % 997, 1)

    def test_inv_mod_edge_cases(self):
        """Test edge cases for modular inverse"""
        # Inverse of 1 is always 1
        self.assertEqual(acl_math.inv_mod(1, 5), 1)
        self.assertEqual(acl_math.inv_mod(1, 1000), 1)

    def test_crt_simple_cases(self):
        """Test simple CRT cases"""
        # x ≡ 2 (mod 3), x ≡ 3 (mod 5)
        # Solution: x ≡ 8 (mod 15)
        x, m = acl_math.crt([2, 3], [3, 5])
        self.assertEqual(x, 8)
        self.assertEqual(m, 15)
        self.assertEqual(x % 3, 2)
        self.assertEqual(x % 5, 3)

    def test_crt_no_solution(self):
        """Test CRT with no solution"""
        # x ≡ 1 (mod 4), x ≡ 3 (mod 4) - no solution
        x, m = acl_math.crt([1, 3], [4, 4])
        self.assertEqual((x, m), (0, 0))

    def test_crt_single_constraint(self):
        """Test CRT with single constraint"""
        x, m = acl_math.crt([5], [7])
        self.assertEqual(x, 5)
        self.assertEqual(m, 7)

    def test_crt_coprime_moduli(self):
        """Test CRT with coprime moduli"""
        # x ≡ 1 (mod 2), x ≡ 2 (mod 3), x ≡ 3 (mod 5)
        x, m = acl_math.crt([1, 2, 3], [2, 3, 5])
        self.assertEqual(m, 30)  # 2 * 3 * 5
        self.assertEqual(x % 2, 1)
        self.assertEqual(x % 3, 2)
        self.assertEqual(x % 5, 3)

    def test_floor_sum_edge_cases(self):
        """Test floor_sum edge cases"""
        # n = 0 should return 0
        self.assertEqual(acl_math.floor_sum(0, 5, 3, 2), 0)

        # m = 1 case
        result = acl_math.floor_sum(5, 1, 0, 0)
        self.assertEqual(result, 0)

    def test_floor_sum_negative_coefficients(self):
        """Test floor_sum with negative coefficients"""
        # Test that negative coefficients are handled properly
        result1 = acl_math.floor_sum(5, 7, -3, 2)
        self.assertIsInstance(result1, int)

        # Test with negative b
        result2 = acl_math.floor_sum(3, 5, 2, -1)
        self.assertIsInstance(result2, int)

    def test_floor_sum_large_values(self):
        """Test floor_sum with larger values"""
        result = acl_math.floor_sum(100, 97, 53, 29)
        # Verify by checking some properties
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)

    def test_inv_gcd_extended_cases(self):
        """Test extended cases for inv_gcd"""
        # Test with a = 0
        g, x = acl_math.inv_gcd(0, 5)
        self.assertEqual(g, 5)
        self.assertEqual(x, 0)

        # Test with larger numbers
        g, x = acl_math.inv_gcd(48, 18)
        self.assertEqual(g, 6)  # gcd(48, 18) = 6

    def test_mathematical_properties(self):
        """Test mathematical properties of the functions"""
        # Test that (a * inv_mod(a, m)) % m == 1 for various coprime pairs
        test_cases = [(3, 7), (5, 11), (7, 13), (11, 17)]
        for a, m in test_cases:
            inv = acl_math.inv_mod(a, m)
            self.assertEqual((a * inv) % m, 1)

        # Test CRT property: if x ≡ r_i (mod m_i), then x % m_i == r_i
        r = [2, 3, 1]
        m = [5, 7, 11]
        x, _ = acl_math.crt(r, m)
        for i in range(len(r)):
            self.assertEqual(x % m[i], r[i])


if __name__ == "__main__":
    unittest.main()
