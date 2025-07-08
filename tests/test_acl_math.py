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



if __name__ == "__main__":
    unittest.main()
