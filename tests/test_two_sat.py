#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import two_sat


class TestTwoSAT(unittest.TestCase):
    """Test cases for two_sat module"""

    def test_two_sat_basic(self):
        """Test basic 2-SAT operations"""
        # Basic test: (x0 OR x1) AND (NOT x0 OR x1) AND (x0 OR NOT x1)
        # This should be satisfiable with x0=True, x1=True
        clauses = [
            (0, True, 1, True),  # x0 OR x1
            (0, False, 1, True),  # NOT x0 OR x1
            (0, True, 1, False),  # x0 OR NOT x1
        ]
        result = two_sat.two_sat(2, clauses)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)

        # Verify the solution satisfies all clauses
        x0, x1 = result[0], result[1]
        self.assertTrue(x0 or x1)  # x0 OR x1
        self.assertTrue(not x0 or x1)  # NOT x0 OR x1
        self.assertTrue(x0 or not x1)  # x0 OR NOT x1

    def test_two_sat_satisfiable(self):
        """Test satisfiable 2-SAT instances"""
        # Test case 1: Simple satisfiable case
        # (x0 OR x1) AND (NOT x0 OR NOT x1)
        clauses = [
            (0, True, 1, True),  # x0 OR x1
            (0, False, 1, False),  # NOT x0 OR NOT x1
        ]
        result = two_sat.two_sat(2, clauses)
        self.assertIsNotNone(result)

        # Verify solution
        x0, x1 = result[0], result[1]
        self.assertTrue(x0 or x1)
        self.assertTrue(not x0 or not x1)

        # Test case 2: More complex satisfiable case
        # (x0 OR x1) AND (x1 OR x2) AND (NOT x0 OR NOT x2)
        clauses = [
            (0, True, 1, True),  # x0 OR x1
            (1, True, 2, True),  # x1 OR x2
            (0, False, 2, False),  # NOT x0 OR NOT x2
        ]
        result = two_sat.two_sat(3, clauses)
        self.assertIsNotNone(result)

        # Verify solution
        x0, x1, x2 = result[0], result[1], result[2]
        self.assertTrue(x0 or x1)
        self.assertTrue(x1 or x2)
        self.assertTrue(not x0 or not x2)

    def test_two_sat_unsatisfiable(self):
        """Test unsatisfiable 2-SAT instances"""
        # Test case 1: Simple unsatisfiable case
        # (x0 OR x0) AND (NOT x0 OR NOT x0) - equivalent to x0 AND NOT x0
        clauses = [
            (0, True, 0, True),  # x0 OR x0 (equivalent to x0)
            (0, False, 0, False),  # NOT x0 OR NOT x0 (equivalent to NOT x0)
        ]
        result = two_sat.two_sat(1, clauses)
        self.assertIsNone(result)

        # Test case 2: More complex unsatisfiable case
        # (x0 OR x1) AND (NOT x0 OR x1) AND (x0 OR NOT x1) AND (NOT x0 OR NOT x1)
        clauses = [
            (0, True, 1, True),  # x0 OR x1
            (0, False, 1, True),  # NOT x0 OR x1
            (0, True, 1, False),  # x0 OR NOT x1
            (0, False, 1, False),  # NOT x0 OR NOT x1
        ]
        result = two_sat.two_sat(2, clauses)
        self.assertIsNone(result)

        # Test case 3: Direct contradiction - force x0 to be both True and False
        # x0 AND NOT x0 - this should be unsatisfiable
        clauses = [
            (0, True, 0, True),  # x0 (force x0 to be True)
            (0, False, 0, False),  # NOT x0 (force x0 to be False)
            (1, True, 1, True),  # x1 (dummy clause to have more variables)
        ]
        result = two_sat.two_sat(2, clauses)
        self.assertIsNone(result)

    def test_single_variable(self):
        """Test single variable cases"""
        # Test: x0 must be True
        clauses = [(0, True, 0, True)]  # x0 OR x0
        result = two_sat.two_sat(1, clauses)
        self.assertIsNotNone(result)
        self.assertTrue(result[0])

        # Test: x0 must be False
        clauses = [(0, False, 0, False)]  # NOT x0 OR NOT x0
        result = two_sat.two_sat(1, clauses)
        self.assertIsNotNone(result)
        self.assertFalse(result[0])

    def test_empty_clauses(self):
        """Test with no clauses (should be satisfiable)"""
        result = two_sat.two_sat(3, [])
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)

    def test_multiple_solutions(self):
        """Test case with multiple valid solutions"""
        # Just x0 OR x1 - multiple solutions possible
        clauses = [(0, True, 1, True)]
        result = two_sat.two_sat(2, clauses)
        self.assertIsNotNone(result)

        # Verify the solution satisfies the constraint
        x0, x1 = result[0], result[1]
        self.assertTrue(x0 or x1)


if __name__ == "__main__":
    unittest.main()
