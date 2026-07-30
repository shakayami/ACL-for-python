#!/usr/bin/env python3

import random
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import convolution

MODS = [998244353, 167772161, 469762049, 754974721]


def naive_convolution(a, b, mod):
    """O(nm) reference implementation."""
    if not a or not b:
        return []
    res = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            res[i + j] = (res[i + j] + x * y) % mod
    return res


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

    def test_empty(self):
        conv = convolution.FFT(998244353)
        self.assertEqual(conv.convolution([], [1, 2, 3]), [])
        self.assertEqual(conv.convolution([1, 2, 3], []), [])
        self.assertEqual(conv.convolution([], []), [])

    def test_against_naive_random(self):
        """Random small cases against the O(nm) reference, over several mods.

        Sizes and coefficient ranges are varied deliberately: convolution
        dispatches between a schoolbook, an integer-packing and an NTT path
        depending on both, so a single size would only cover one of them.
        """
        rng = random.Random(998244353)
        for mod in MODS:
            conv = convolution.FFT(mod)
            for _ in range(60):
                n = rng.randint(1, 200)
                m = rng.randint(1, 200)
                vmax = rng.choice([2, 256, mod])
                a = [rng.randrange(vmax) for _ in range(n)]
                b = [rng.randrange(vmax) for _ in range(m)]
                self.assertEqual(
                    conv.convolution(a, b), naive_convolution(a, b, mod), (mod, n, m)
                )

    def test_unnormalized_input(self):
        """Negative coefficients and coefficients >= mod are reduced."""
        mod = 998244353
        conv = convolution.FFT(mod)
        rng = random.Random(7)
        for n, m in [(3, 4), (60, 60), (200, 5)]:
            a = [rng.randrange(-3 * mod, 3 * mod) for _ in range(n)]
            b = [rng.randrange(-3 * mod, 3 * mod) for _ in range(m)]
            self.assertEqual(conv.convolution(a, b), naive_convolution(a, b, mod))

    def test_zero_coefficients(self):
        mod = 998244353
        conv = convolution.FFT(mod)
        n = 100
        self.assertEqual(conv.convolution([0] * n, [0] * n), [0] * (2 * n - 1))
        self.assertEqual(conv.convolution([0] * n, [1] * n), [0] * (2 * n - 1))

    def test_large_and_lopsided(self):
        """Cases big enough to reach the NTT and integer-packing paths."""
        mod = 998244353
        conv = convolution.FFT(mod)
        rng = random.Random(11)
        for n, m in [(1, 3000), (3000, 1), (2000, 17), (1000, 1000), (4096, 4096)]:
            a = [rng.randrange(mod) for _ in range(n)]
            b = [rng.randrange(mod) for _ in range(m)]
            c = conv.convolution(a, b)
            self.assertEqual(len(c), n + m - 1)
            # Spot-check individual coefficients rather than the whole
            # O(nm) reference, which would be too slow at these sizes.
            for k in (0, (n + m - 1) // 2, n + m - 2):
                expect = sum(
                    a[i] * b[k - i] for i in range(max(0, k - m + 1), min(n - 1, k) + 1)
                )
                self.assertEqual(c[k], expect % mod, (n, m, k))

    def test_butterfly_round_trip(self):
        """butterfly followed by butterfly_inv is the identity times n."""
        mod = 998244353
        conv = convolution.FFT(mod)
        rng = random.Random(3)
        for h in (1, 2, 3, 8):
            n = 1 << h
            a = [rng.randrange(mod) for _ in range(n)]
            work = a[:]
            conv.butterfly(work)
            conv.butterfly_inv(work)
            inv_n = pow(n, mod - 2, mod)
            self.assertEqual([x * inv_n % mod for x in work], a)


if __name__ == "__main__":
    unittest.main()
