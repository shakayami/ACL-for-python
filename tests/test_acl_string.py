#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from acl_string import String


class TestSuffixArray(unittest.TestCase):
    def _check_sa(self, s, sa):
        """suffix_array の正当性を検証: SA が辞書順ソートになっているか"""
        n = len(s)
        self.assertEqual(len(sa), n)
        self.assertEqual(sorted(sa), list(range(n)))
        suffixes = [s[i:] for i in sa]
        for i in range(len(suffixes) - 1):
            self.assertLessEqual(suffixes[i], suffixes[i + 1])

    def test_empty(self):
        self.assertEqual(String("").suffix_array(), [])

    def test_single_char(self):
        self.assertEqual(String("a").suffix_array(), [0])

    def test_two_chars_sorted(self):
        self.assertEqual(String("ab").suffix_array(), [0, 1])

    def test_two_chars_reversed(self):
        self.assertEqual(String("ba").suffix_array(), [1, 0])

    def test_all_same(self):
        sa = String("aaaa").suffix_array()
        self._check_sa("aaaa", sa)

    def test_abab(self):
        self.assertEqual(String("abab").suffix_array(), [2, 0, 3, 1])

    def test_known_mississippi(self):
        s = "mississippi"
        sa = String(s).suffix_array()
        self._check_sa(s, sa)

    def test_known_abcbcba(self):
        s = "abcbcba"
        sa = String(s).suffix_array()
        self._check_sa(s, sa)

    def test_integer_list(self):
        s = [3, 1, 4, 1, 5, 9, 2, 6]
        sa = String(s).suffix_array()
        self._check_sa(s, sa)

    def test_integer_list_all_same(self):
        s = [0, 0, 0, 0]
        sa = String(s).suffix_array()
        self._check_sa(s, sa)

    def test_practice2_i(self):
        """ACL practice2 問題 I: 異なる部分文字列の数"""
        cases = [
            ("abcbcba", 21),
            ("mississippi", 53),
            ("ababacaca", 33),
            ("aaaaa", 5),
        ]
        for s, expected in cases:
            with self.subTest(s=s):
                st = String(s)
                sa = st.suffix_array()
                res = (len(s) * (len(s) + 1)) // 2
                for x in st.lcp_array(sa):
                    res -= x
                self.assertEqual(res, expected)


class TestLcpArray(unittest.TestCase):
    def test_basic(self):
        st = String("abab")
        sa = st.suffix_array()
        self.assertEqual(st.lcp_array(sa), [2, 0, 1])

    def test_auto_sa(self):
        # sa を省略すると内部で suffix_array() を計算する
        self.assertEqual(String("abab").lcp_array(), [2, 0, 1])

    def test_all_same(self):
        st = String("aaaa")
        sa = st.suffix_array()
        lcp = st.lcp_array(sa)
        # sa = [3,2,1,0] ("a","aa","aaa","aaaa") -> LCP は 1, 2, 3
        self.assertEqual(lcp, [1, 2, 3])

    def test_all_distinct(self):
        st = String("abcd")
        sa = st.suffix_array()
        lcp = st.lcp_array(sa)
        self.assertEqual(lcp, [0, 0, 0])

    def test_single_char(self):
        st = String("a")
        sa = st.suffix_array()
        self.assertEqual(st.lcp_array(sa), [])

    def test_mississippi(self):
        s = "mississippi"
        st = String(s)
        sa = st.suffix_array()
        lcp = st.lcp_array(sa)
        self.assertEqual(len(lcp), len(s) - 1)
        # 各 LCP 値は非負かつ対応する suffix の長さを超えない
        for i, v in enumerate(lcp):
            self.assertGreaterEqual(v, 0)
            self.assertLessEqual(v, min(len(s) - sa[i], len(s) - sa[i + 1]))


class TestZAlgorithm(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(String("").z_algorithm(), [])

    def test_single_char(self):
        self.assertEqual(String("a").z_algorithm(), [1])

    def test_all_same(self):
        self.assertEqual(String("aaaa").z_algorithm(), [4, 3, 2, 1])

    def test_aabxaa(self):
        self.assertEqual(String("aabxaa").z_algorithm(), [6, 1, 0, 0, 2, 1])

    def test_abcabcabc(self):
        self.assertEqual(String("abcabcabc").z_algorithm(), [9, 0, 0, 6, 0, 0, 3, 0, 0])

    def test_abacaba(self):
        self.assertEqual(String("abacaba").z_algorithm(), [7, 0, 1, 0, 3, 0, 1])

    def test_all_distinct(self):
        z = String("abcde").z_algorithm()
        self.assertEqual(z[0], 5)
        for v in z[1:]:
            self.assertEqual(v, 0)

    def test_z_property(self):
        """z[i] は s[i:i+z[i]] == s[0:z[i]] を満たす"""
        s = "aababcabc"
        z = String(s).z_algorithm()
        self.assertEqual(z[0], len(s))
        for i in range(1, len(s)):
            self.assertEqual(s[: z[i]], s[i : i + z[i]])

    def test_pattern_search(self):
        """Z アルゴリズムによるパターン検索"""
        text = "abcabcabc"
        pat = "abc"
        combined = pat + "$" + text
        z = String(combined).z_algorithm()
        plen = len(pat)
        matches = [i - plen - 1 for i in range(plen + 1, len(combined)) if z[i] >= plen]
        self.assertEqual(matches, [0, 3, 6])


class TestStringProtocol(unittest.TestCase):
    def test_len(self):
        self.assertEqual(len(String("hello")), 5)
        self.assertEqual(len(String("")), 0)

    def test_getitem(self):
        st = String("hello")
        self.assertEqual(st[0], "h")
        self.assertEqual(st[-1], "o")
        self.assertEqual(st[1:3], "el")

    def test_repr(self):
        self.assertIn("hello", repr(String("hello")))

    def test_str(self):
        self.assertIn("hello", str(String("hello")))

    def test_integer_list_getitem(self):
        st = String([1, 2, 3])
        self.assertEqual(st[0], 1)
        self.assertEqual(st[1:], [2, 3])


if __name__ == "__main__":
    unittest.main()
