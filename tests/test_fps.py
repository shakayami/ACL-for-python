#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fps
import random


class TestFPS(unittest.TestCase):
    """Test cases for fps module"""

    def test_fps_basic(self):
        A = fps.FPS([1, 2, 3])
        B = fps.FPS([4, 5, 6, 7])
        self.assertEqual(A + B, fps.FPS([5, 7, 9, 7]))
        self.assertEqual(A - B, fps.FPS([998244350, 998244350, 998244350, 998244346]))
        self.assertEqual(A * B, fps.FPS([4, 13, 28, 34, 32, 21]))
        self.assertEqual(
            A / B,
            fps.FPS([748683265, 811073537, 857866241, 892960768, 928055297, 963149825]),
        )
        self.assertEqual(A >> 1, fps.FPS([2, 3, 0]))
        self.assertEqual(A << 1, fps.FPS([0, 1, 2, 3]))
        A >>= 1
        self.assertEqual(A, fps.FPS([2, 3, 0]))
        A <<= 1
        self.assertEqual(A, fps.FPS([0, 2, 3, 0]))
        A = fps.FPS([1, 2, 3])
        A += B
        self.assertEqual(A, fps.FPS([5, 7, 9, 7]))
        A = fps.FPS([1, 2, 3])
        A -= B
        self.assertEqual(A, fps.FPS([998244350, 998244350, 998244350, 998244346]))
        A = fps.FPS([1, 2, 3])
        A *= B
        self.assertEqual(A, fps.FPS([4, 13, 28, 34, 32, 21]))
        A = fps.FPS([1, 2, 3])
        A /= B
        self.assertEqual(
            A,
            fps.FPS([748683265, 811073537, 857866241, 892960768, 928055297, 963149825]),
        )
        A = fps.FPS([1, 2, 3])
        self.assertEqual(A.diff(), fps.FPS([2, 6]))
        A = fps.FPS([1, 2, 3])
        self.assertEqual(A.integral(), fps.FPS([0, 1, 1, 1]))

    def test_fps_log(self):
        A = fps.FPS([1, 1, 499122179, 166374064, 291154613])
        self.assertEqual(A.log().resize(5), fps.FPS([0, 1, 2, 3, 4]))

    def test_fps_exp(self):
        A = fps.FPS([0, 1, 2, 3, 4])
        self.assertEqual(
            A.exp().resize(5), fps.FPS([1, 1, 499122179, 166374064, 291154613])
        )

    def test_fps_exp_log(self):
        N = 10**4
        mod = 998244353
        seq = [0] + [random.randrange(mod) for i in range(N - 1)]
        A = fps.FPS(seq)
        B = A.exp()
        C = B.log()
        D = C.resize(N)
        self.assertEqual(A, D)

    def test_fps_log_exp(self):
        N = 10**4
        mod = 998244353
        seq = [1] + [random.randrange(mod) for i in range(N - 1)]
        A = fps.FPS(seq)
        B = A.log()
        C = B.exp()
        D = C.resize(N)
        self.assertEqual(A, D)

    def test_sqrt(self):
        N = 10**4
        mod = 998244353
        seq = [pow(random.randrange(1, mod), 2, mod)] + [
            random.randrange(mod) for i in range(N - 1)
        ]
        A = fps.FPS(seq)
        B = A.sqrt()
        C = B * B
        D = C.resize(N)
        self.assertEqual(A, D)

    def test_fps_inverse(self):
        A = fps.FPS([5, 4, 3, 2, 1])
        self.assertEqual(
            A.inv(), fps.FPS([598946612, 718735934, 862483121, 635682004, 163871793])
        )

    def test_fps_pow(self):
        A = fps.FPS([0, 0, 9, 12])
        self.assertEqual(A.powfps(3), fps.FPS([0, 0, 0, 0]))
        A = fps.FPS([1, 1])
        self.assertEqual(A.powfps(2), fps.FPS([1, 2]))
        A = fps.FPS([0, 0])
        self.assertEqual(A.powfps(0), fps.FPS([1, 0]))


if __name__ == "__main__":
    unittest.main()
