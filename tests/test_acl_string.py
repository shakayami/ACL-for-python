#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import acl_string


class TestACLString(unittest.TestCase):
    """Test cases for acl_string module"""

    def practice2_i(self, S, answer):
        sa = acl_string.string.suffix_array(S)
        res = (len(S) * (len(S) + 1)) // 2
        for x in acl_string.string.lcp_array(S, sa):
            res -= x
        self.assertEqual(res, answer)

    def test_practice2_i(self):
        self.practice2_i("abcbcba", 21)
        self.practice2_i("mississippi", 53)
        self.practice2_i("ababacaca", 33)
        self.practice2_i("aaaaa", 5)

    def test_suffix_array(self):
        """Test suffix array functionality"""
        # TODO: Add test cases for suffix array
        pass

    def test_z_algorithm(self):
        """Test Z algorithm functionality"""
        # TODO: Add test cases for Z algorithm
        pass

    def test_lcp_array(self):
        """Test LCP array functionality"""
        # TODO: Add test cases for LCP array
        pass


if __name__ == "__main__":
    unittest.main()
