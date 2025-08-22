#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import prime_fact


class TestPrimeFact(unittest.TestCase):
    """Test cases for prime_fact module"""

    def test_prime_factorization(self):
        """Test prime factorization functionality"""
        # TODO: Add test cases for prime factorization
        pass

    def is_prime_example(self):
        numList=[1,2,3,4,998244353,1000000000000000000]
        ansList=[False,True,True,False,True,False]
        for n,f in zip(numList,ansList):
            self.assertEqual(prime_fact.is_probable_prime(n),f)

    def test_is_prime(self):
        self.is_prime_example()

    def test_divisors(self):
        """Test divisor enumeration"""
        # TODO: Add test cases for divisor enumeration
        pass

    def test_euler_phi(self):
        """Test Euler's totient function"""
        # TODO: Add test cases for Euler's totient function
        pass

    def test_prime_factorization_small_numbers(self):
        """Test prime factorization of small numbers"""
        # Test small primes
        self.assertEqual(dict(prime_fact.prime_fact(2)), {2: 1})
        self.assertEqual(dict(prime_fact.prime_fact(3)), {3: 1})
        self.assertEqual(dict(prime_fact.prime_fact(5)), {5: 1})

        # Test composite numbers
        self.assertEqual(dict(prime_fact.prime_fact(6)), {2: 1, 3: 1})
        self.assertEqual(dict(prime_fact.prime_fact(12)), {2: 2, 3: 1})
        self.assertEqual(dict(prime_fact.prime_fact(18)), {2: 1, 3: 2})

    def test_prime_factorization_edge_cases(self):
        """Test edge cases for prime factorization"""
        # Test 1
        self.assertEqual(dict(prime_fact.prime_fact(1)), {})

        # Test powers of 2
        self.assertEqual(dict(prime_fact.prime_fact(8)), {2: 3})
        self.assertEqual(dict(prime_fact.prime_fact(16)), {2: 4})

        # Test squares of primes
        self.assertEqual(dict(prime_fact.prime_fact(49)), {7: 2})
        self.assertEqual(dict(prime_fact.prime_fact(121)), {11: 2})

    def test_is_probable_prime(self):
        """Test primality testing"""
        # Test known primes
        known_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        for p in known_primes:
            self.assertTrue(prime_fact.is_probable_prime(p))

        # Test known composites
        known_composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20]
        for c in known_composites:
            self.assertFalse(prime_fact.is_probable_prime(c))

        # Test edge cases
        self.assertFalse(prime_fact.is_probable_prime(1))
        self.assertTrue(prime_fact.is_probable_prime(2))

    def test_divisors_basic(self):
        """Test basic divisor enumeration"""
        # Test 1
        divisors_1 = sorted(prime_fact.divisors(1))
        self.assertEqual(divisors_1, [1])

        # Test 6 = 2 * 3
        divisors_6 = sorted(prime_fact.divisors(6))
        self.assertEqual(divisors_6, [1, 2, 3, 6])

        # Test 12 = 2^2 * 3
        divisors_12 = sorted(prime_fact.divisors(12))
        self.assertEqual(divisors_12, [1, 2, 3, 4, 6, 12])

    def test_divisors_prime_powers(self):
        """Test divisors of prime powers"""
        # Test 8 = 2^3
        divisors_8 = sorted(prime_fact.divisors(8))
        self.assertEqual(divisors_8, [1, 2, 4, 8])

        # Test 9 = 3^2
        divisors_9 = sorted(prime_fact.divisors(9))
        self.assertEqual(divisors_9, [1, 3, 9])

    def test_totient_basic(self):
        """Test Euler's totient function"""
        # φ(1) = 1
        self.assertEqual(prime_fact.totient(1), 1)

        # φ(p) = p-1 for prime p
        self.assertEqual(prime_fact.totient(2), 1)
        self.assertEqual(prime_fact.totient(3), 2)
        self.assertEqual(prime_fact.totient(5), 4)
        self.assertEqual(prime_fact.totient(7), 6)

        # φ(6) = φ(2*3) = 6*(1-1/2)*(1-1/3) = 2
        self.assertEqual(prime_fact.totient(6), 2)

        # φ(12) = φ(2^2*3) = 12*(1-1/2)*(1-1/3) = 4
        self.assertEqual(prime_fact.totient(12), 4)

    def test_lcm_basic(self):
        """Test least common multiple"""
        # lcm(6, 8) = 24
        self.assertEqual(prime_fact.lcm(6, 8), 24)

        # lcm(12, 18) = 36
        self.assertEqual(prime_fact.lcm(12, 18), 36)

        # lcm with 1
        self.assertEqual(prime_fact.lcm(1, 5), 5)
        self.assertEqual(prime_fact.lcm(7, 1), 7)

        # lcm of coprime numbers
        self.assertEqual(prime_fact.lcm(3, 5), 15)
        self.assertEqual(prime_fact.lcm(7, 11), 77)

    def test_larger_numbers(self):
        """Test with larger numbers"""
        # Test a larger composite number
        pf_100 = dict(prime_fact.prime_fact(100))
        self.assertEqual(pf_100, {2: 2, 5: 2})

        # Test totient of 100
        self.assertEqual(prime_fact.totient(100), 40)

        # Test number of divisors of 100
        divisors_100 = prime_fact.divisors(100)
        self.assertEqual(len(divisors_100), 9)  # (2+1)*(2+1) = 9

    def test_mathematical_properties(self):
        """Test mathematical properties"""
        # Test that all prime factors actually divide the number
        for n in [60, 72, 90]:
            factors = prime_fact.prime_fact(n)
            for p, e in factors.items():
                self.assertEqual(n % p, 0)
                self.assertGreater(e, 0)

        # Test that divisors actually divide the number
        for n in [24, 30, 36]:
            divs = prime_fact.divisors(n)
            for d in divs:
                self.assertEqual(n % d, 0)

        # Test lcm property: lcm(a,b) * gcd(a,b) = a * b
        from math import gcd

        test_pairs = [(12, 18), (15, 20), (7, 11)]
        for a, b in test_pairs:
            self.assertEqual(prime_fact.lcm(a, b) * gcd(a, b), a * b)

    def test_consistency_checks(self):
        """Test consistency between different functions"""
        # Test that prime factorization reconstructs the original number
        test_numbers = [24, 36, 48, 60]
        for n in test_numbers:
            factors = prime_fact.prime_fact(n)
            reconstructed = 1
            for p, e in factors.items():
                reconstructed *= p**e
            self.assertEqual(reconstructed, n)


if __name__ == "__main__":
    unittest.main()
