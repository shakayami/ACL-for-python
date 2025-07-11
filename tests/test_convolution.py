#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import convolution


class TestConvolution(unittest.TestCase):
    """Test cases for convolution module"""

    def practice2_f(self, N, M, A, B, ans):
        CONV = convolution.FFT(998244353)
        self.assertEqual(CONV.convolution(A, B), ans)

    def test_practice2_f(self):
        self.practice2_f(
            4, 5, [1, 2, 3, 4], [5, 6, 7, 8, 9], [5, 16, 34, 60, 70, 70, 59, 36]
        )
        self.practice2_f(1, 1, [10000000], [10000000], [871938225])


if __name__ == "__main__":
    unittest.main()
