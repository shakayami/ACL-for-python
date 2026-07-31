"""Correctness tests for the benchmark workloads.

A benchmark is only meaningful if the code it times actually solves the
problem it claims to.  Without these tests an "optimisation" that quietly
breaks the library would show up as a large, celebrated speedup.

Each test drives a ``benchmarks.workloads.run_*`` function with hand-built
inputs in the same shape its ``build_*`` counterpart produces, and checks the
answer against a naive reference.
"""

import copy
import importlib
import itertools
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "benchmarks"
    ),
)

import workloads as W  # noqa: E402

MOD = W.MOD


class TestUniformPair(unittest.TestCase):
    def test_returns_non_empty_subinterval(self):
        r = random.Random(0)
        for n in (1, 2, 5, 50):
            for _ in range(200):
                l, rr = W._uniform_pair(r, 0, n)
                self.assertTrue(0 <= l < rr <= n, (l, rr, n))

    def test_covers_both_endpoints(self):
        r = random.Random(1)
        seen = {W._uniform_pair(r, 0, 3) for _ in range(500)}
        self.assertEqual(len(seen), 6)  # all C(4, 2) pairs


class TestDataStructureWorkloads(unittest.TestCase):
    def test_point_add_range_sum(self):
        r = random.Random(2)
        n = 40
        a = [r.randint(0, 100) for _ in range(n)]
        queries = []
        for _ in range(200):
            if r.randint(0, 1) == 0:
                queries.append((0, r.randrange(n), r.randint(0, 100)))
            else:
                queries.append((1,) + W._uniform_pair(r, 0, n))

        naive = list(a)
        expected = 0
        for t, x, y in queries:
            if t == 0:
                naive[x] += y
            else:
                expected += sum(naive[x:y])

        self.assertEqual(W.run_point_add_range_sum(n, a, queries), expected)

    def test_staticrmq(self):
        r = random.Random(3)
        n = 37
        a = [r.randint(0, 10**9) for _ in range(n)]
        queries = [W._uniform_pair(r, 0, n) for _ in range(200)]

        expected = 0
        for l, rr in queries:
            expected ^= min(a[l:rr])

        self.assertEqual(W.run_staticrmq(a, queries), expected)

    def test_point_set_range_composite(self):
        r = random.Random(4)
        n = 33
        f = [(r.randint(1, MOD - 1), r.randint(0, MOD - 1)) for _ in range(n)]
        queries = []
        for _ in range(150):
            if r.randint(0, 1) == 0:
                queries.append(
                    (0, r.randrange(n), r.randint(1, MOD - 1), r.randint(0, MOD - 1))
                )
            else:
                l, rr = W._uniform_pair(r, 0, n)
                queries.append((1, l, rr, r.randint(0, MOD - 1)))

        naive = list(f)
        expected = 0
        for query in queries:
            if query[0] == 0:
                _, p, c, d = query
                naive[p] = (c, d)
            else:
                _, l, rr, x = query
                value = x
                # f_{r-1}(f_{r-2}(...f_l(x)))
                for i in range(l, rr):
                    value = (naive[i][0] * value + naive[i][1]) % MOD
                expected += value

        self.assertEqual(W.run_point_set_range_composite(f, queries), expected)

    def test_range_affine_range_sum(self):
        r = random.Random(5)
        n = 29
        a = [r.randint(0, MOD - 1) for _ in range(n)]
        queries = []
        for _ in range(150):
            l, rr = W._uniform_pair(r, 0, n)
            if r.randint(0, 1) == 0:
                queries.append((0, l, rr, r.randint(1, MOD - 1), r.randint(0, MOD - 1)))
            else:
                queries.append((1, l, rr, 0, 0))

        naive = list(a)
        expected = 0
        for t, l, rr, b, c in queries:
            if t == 0:
                for i in range(l, rr):
                    naive[i] = (b * naive[i] + c) % MOD
            else:
                expected += sum(naive[l:rr]) % MOD

        self.assertEqual(W.run_range_affine_range_sum(a, queries), expected)

    def test_unionfind(self):
        r = random.Random(6)
        n = 30
        queries = [
            (r.randint(0, 1), r.randrange(n), r.randrange(n)) for _ in range(200)
        ]

        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                x = parent[x]
            return x

        expected = 0
        for t, u, v in queries:
            if t == 0:
                parent[find(u)] = find(v)
            else:
                expected += find(u) == find(v)

        self.assertEqual(W.run_unionfind(n, queries), expected)


class TestGraphWorkloads(unittest.TestCase):
    def test_scc_component_count(self):
        # two 3-cycles joined by a one-way bridge, plus an isolated vertex
        edges = [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (2, 3)]
        self.assertEqual(W.run_scc(7, edges), 3)

    def test_two_sat_satisfiable(self):
        # (x0 or x1) and (not x0 or x1)  ->  satisfiable
        clause = [(0, True, 1, True), (0, False, 1, True)]
        self.assertGreaterEqual(W.run_two_sat(2, clause), 0)

    def test_two_sat_unsatisfiable(self):
        clause = [
            (0, True, 0, True),
            (0, False, 0, False),
        ]
        self.assertEqual(W.run_two_sat(1, clause), -1)

    def test_bipartitematching(self):
        r = random.Random(7)
        left = right = 6
        edges = sorted({(r.randrange(left), r.randrange(right)) for _ in range(18)})

        # naive Kuhn
        adj = [[] for _ in range(left)]
        for u, v in edges:
            adj[u].append(v)
        match = [-1] * right

        def try_kuhn(u, seen):
            for v in adj[u]:
                if seen[v]:
                    continue
                seen[v] = True
                if match[v] == -1 or try_kuhn(match[v], seen):
                    match[v] = u
                    return True
            return False

        expected = sum(try_kuhn(u, [False] * right) for u in range(left))

        self.assertEqual(W.run_bipartitematching(left, right, edges), expected)

    def test_assignment(self):
        r = random.Random(8)
        n = 5
        a = [[r.randint(-1000, 1000) for _ in range(n)] for _ in range(n)]
        expected = min(
            sum(a[i][p[i]] for i in range(n)) for p in itertools.permutations(range(n))
        )
        self.assertEqual(W.run_assignment(n, a), expected)


class TestMathWorkloads(unittest.TestCase):
    def test_convolution_mod(self):
        r = random.Random(9)
        # Above 40 elements so this exercises the NTT path, not the naive
        # fallback that FFT.convolution takes for small inputs.
        a = [r.randint(0, MOD - 1) for _ in range(70)]
        b = [r.randint(0, MOD - 1) for _ in range(53)]
        c = [0] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                c[i + j] = (c[i + j] + x * y) % MOD
        self.assertEqual(W.run_convolution_mod(a, b), c[0] ^ c[-1])

    def test_inv_of_formal_power_series(self):
        r = random.Random(10)
        n = 32
        a = [r.randint(1, MOD - 1)] + [r.randint(0, MOD - 1) for _ in range(n - 1)]
        inv = W.fps_mod.FPS(a).inv(n)
        product = (W.fps_mod.FPS(a) * inv).resize(n).Func
        self.assertEqual(product, [1] + [0] * (n - 1))
        self.assertEqual(W.run_inv_of_formal_power_series(a), inv.Func[-1])

    def test_exp_log_round_trip(self):
        r = random.Random(11)
        n = 32
        a = [0] + [r.randint(0, MOD - 1) for _ in range(n - 1)]
        exp = W.fps_mod.FPS(a).exp(n)
        self.assertEqual(exp.Func[0], 1)
        self.assertEqual(exp.log().resize(n).Func, a)
        self.assertEqual(W.run_exp_of_formal_power_series(a), exp.Func[-1])

    def test_log_of_formal_power_series(self):
        r = random.Random(12)
        n = 32
        a = [1] + [r.randint(0, MOD - 1) for _ in range(n - 1)]
        expected = W.fps_mod.FPS(a).log().resize(n)
        self.assertEqual(expected.Func[0], 0)
        self.assertEqual(W.run_log_of_formal_power_series(a), expected.Func[-1])

    def test_sum_of_floor_of_linear(self):
        r = random.Random(13)
        cases = []
        for _ in range(30):
            n = r.randint(1, 60)
            m = r.randint(1, 60)
            cases.append((n, m, r.randrange(m), r.randrange(m)))
        expected = sum(sum((a * i + b) // m for i in range(n)) for n, m, a, b in cases)
        self.assertEqual(W.run_sum_of_floor_of_linear(cases), expected)

    def test_primality_test(self):
        values = list(range(1, 300))

        def naive(n):
            if n < 2:
                return False
            return all(n % d for d in range(2, int(n**0.5) + 1))

        self.assertEqual(
            W.run_primality_test(values), sum(1 for n in values if naive(n))
        )

    def test_factorize(self):
        values = [10**18 - i for i in range(3)]
        self.assertEqual(
            W.run_factorize(values),
            sum(sum(W.prime_fact_mod.prime_fact(n).values()) for n in values),
        )
        for n in values:
            product = 1
            for p, e in W.prime_fact_mod.prime_fact(n).items():
                self.assertTrue(W.prime_fact_mod.is_probable_prime(p))
                product *= p**e
            self.assertEqual(product, n)


class TestStringWorkloads(unittest.TestCase):
    def test_suffixarray(self):
        s = "mississippi"
        expected = sorted(range(len(s)), key=lambda i: s[i:])
        sa = W.acl_string_mod.String(s).suffix_array()
        self.assertEqual(sa, expected)
        self.assertEqual(W.run_suffixarray(s), expected[0] ^ expected[-1])

    def test_zalgorithm(self):
        s = "abacabadabacaba"
        z = []
        for i in range(len(s)):
            k = 0
            while i + k < len(s) and s[k] == s[i + k]:
                k += 1
            z.append(k)
        self.assertEqual(W.run_zalgorithm(s), sum(z))

    def test_number_of_substrings(self):
        r = random.Random(14)
        s = "".join(r.choice("ab") for _ in range(40))
        expected = len(
            {s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)}
        )
        self.assertEqual(W.run_number_of_substrings(s), expected)


class TestRegistry(unittest.TestCase):
    def test_every_module_is_covered(self):
        modules = {
            "segtree",
            "lazysegtree",
            "dsu",
            "maxflow",
            "mincostflow",
            "convolution",
            "scc",
            "fps",
            "fenwicktree",
            "acl_math",
            "acl_string",
            "prime_fact",
            "two_sat",
        }
        self.assertEqual(modules - {w.module for w in W.BENCHMARKS}, set())

    def test_library_checker_workloads_declare_a_problem(self):
        for w in W.LIBRARY_CHECKER_BENCHMARKS:
            self.assertTrue(w.problem, w.name)
            self.assertEqual(w.name, w.problem)
            self.assertTrue(w.url.startswith("https://judge.yosupo.jp/problem/"))

    def test_extra_workloads_declare_no_problem(self):
        for w in W.EXTRA_BENCHMARKS:
            self.assertIsNone(w.problem, w.name)
            self.assertTrue(w.name.startswith("extra_"))

    def test_names_are_unique(self):
        names = [w.name for w in W.BENCHMARKS]
        self.assertEqual(len(names), len(set(names)))

    def test_cost_factor_matches_the_registry(self):
        self.assertEqual(set(W.COST_FACTOR), {w.name for w in W.BENCHMARKS})

    def test_effective_scale_never_exceeds_the_judge_constraints(self):
        for w in W.BENCHMARKS:
            self.assertTrue(0 < w.effective_scale <= 1, w.name)

    def test_max_scale_pins_every_workload_to_the_maximum(self):
        original = W.SCALE
        try:
            W.SCALE = float("inf")
            for w in W.BENCHMARKS:
                self.assertEqual(w.effective_scale, 1.0, w.name)
        finally:
            W.SCALE = original

    def test_runners_do_not_mutate_their_inputs(self):
        """pytest-benchmark reuses one ``build()`` result across every round
        and warmup, so a runner that mutated its arguments would time a
        different problem each round. Checked at a tiny scale."""
        os.environ["ACL_BENCH_SCALE"] = "0.0005"
        try:
            importlib.reload(W)
            for w in W.BENCHMARKS:
                args = w.build()
                before = copy.deepcopy(args)
                w.run(*args)
                self.assertEqual(args, before, w.name)
        finally:
            del os.environ["ACL_BENCH_SCALE"]
            importlib.reload(W)

    def test_unpacks_as_a_triple(self):
        name, build, run = W.BENCHMARKS[0]
        self.assertEqual(name, W.BENCHMARKS[0].name)
        self.assertTrue(callable(build) and callable(run))


if __name__ == "__main__":
    unittest.main()
