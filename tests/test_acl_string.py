#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from acl_string import String


class TestACLString(unittest.TestCase):
    def practice2_i(self, s, answer):
        st = String(s)
        sa = st.suffix_array()
        res = (len(s) * (len(s) + 1)) // 2
        for x in st.lcp_array(sa):
            res -= x
        self.assertEqual(res, answer)

    def test_practice2_i(self):
        self.practice2_i("abcbcba", 21)
        self.practice2_i("mississippi", 53)
        self.practice2_i("ababacaca", 33)
        self.practice2_i("aaaaa", 5)

    def test_suffix_array(self):
        sa = String("abab").suffix_array()
        self.assertEqual(sa, [2, 0, 3, 1])

    def test_lcp_array(self):
        st = String("abab")
        sa = st.suffix_array()
        lcp = st.lcp_array(sa)
        self.assertEqual(lcp, [2, 0, 1])

    def test_lcp_array_auto_sa(self):
        # lcp_array without explicit sa computes it internally
        lcp = String("abab").lcp_array()
        self.assertEqual(lcp, [2, 0, 1])

    def test_z_algorithm(self):
        self.assertEqual(String("aabxaa").z_algorithm(), [6, 1, 0, 0, 2, 1])
        self.assertEqual(String("abcabcabc").z_algorithm(), [9, 0, 0, 6, 0, 0, 3, 0, 0])

    def test_len_and_getitem(self):
        st = String("hello")
        self.assertEqual(len(st), 5)
        self.assertEqual(st[0], "h")
        self.assertEqual(st[-1], "o")


if __name__ == "__main__":
    unittest.main()
