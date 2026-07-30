"""Deterministic workloads shared by the time (pytest-benchmark) and memory
(tracemalloc) benchmarks, so both measure exactly the same operations.

Data sizes are intentionally large (and randomly generated) because these
benchmarks only care about wall-clock/memory cost, not about producing a
particular result. Each workload also drives every public method the
corresponding module exposes (e.g. dsu exercises leader/merge/same/size/
groups) so a regression in any single method is caught, not just the ones
that happened to be exercised before.
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import segtree as segtree_mod
import lazysegtree as lazysegtree_mod
import dsu as dsu_mod
import maxflow as maxflow_mod
import mincostflow as mincostflow_mod
import convolution as convolution_mod
import scc as scc_mod
import fps as fps_mod
import fenwicktree as fenwicktree_mod
import acl_math as acl_math_mod
import acl_string as acl_string_mod
import prime_fact as prime_fact_mod
import two_sat as two_sat_mod

MOD = 998244353


def _rng(seed):
    return random.Random(seed)


# ---------------------------------------------------------------------------
# segtree: set / get / prod / all_prod / max_right / min_left on a large array
# ---------------------------------------------------------------------------
def build_segtree_workload():
    r = _rng(1)
    n, q = 200_000, 200_000
    values = [r.randint(1, 10**9) for _ in range(n)]
    queries = []
    for _ in range(q):
        choice = r.random()
        if choice < 0.3:
            queries.append(("set", r.randrange(n), r.randint(1, 10**9)))
        elif choice < 0.5:
            queries.append(("get", r.randrange(n)))
        elif choice < 0.75:
            l = r.randrange(n)
            queries.append(("prod", l, r.randrange(l, n + 1)))
        elif choice < 0.8:
            queries.append(("all_prod",))
        elif choice < 0.9:
            queries.append(("max_right", r.randrange(n + 1), r.randint(1, 10**9)))
        else:
            queries.append(("min_left", r.randrange(n + 1), r.randint(1, 10**9)))
    return values, queries


def run_segtree(values, queries):
    seg = segtree_mod.segtree(list(values), max, -1)
    for q in queries:
        op = q[0]
        if op == "set":
            seg.set(q[1], q[2])
        elif op == "get":
            seg.get(q[1])
        elif op == "prod":
            seg.prod(q[1], q[2])
        elif op == "all_prod":
            seg.all_prod()
        elif op == "max_right":
            threshold = q[2]
            seg.max_right(q[1], lambda x, th=threshold: x <= th)
        else:
            threshold = q[2]
            seg.min_left(q[1], lambda x, th=threshold: x <= th)
    return seg


# ---------------------------------------------------------------------------
# lazysegtree: set / get / prod / all_prod / apply_point / apply / max_right /
# min_left on a large array (range-add, range-min)
# ---------------------------------------------------------------------------
def build_lazysegtree_workload():
    r = _rng(2)
    n, q = 100_000, 100_000
    values = [0] * n
    queries = []
    for _ in range(q):
        choice = r.random()
        if choice < 0.25:
            l = r.randrange(n)
            rr = r.randrange(l, n + 1)
            queries.append(("apply", l, rr, r.randint(-1000, 1000)))
        elif choice < 0.45:
            l = r.randrange(n)
            rr = r.randrange(l, n + 1)
            queries.append(("prod", l, rr))
        elif choice < 0.55:
            queries.append(("set", r.randrange(n), r.randint(-1000, 1000)))
        elif choice < 0.65:
            queries.append(("get", r.randrange(n)))
        elif choice < 0.7:
            queries.append(("all_prod",))
        elif choice < 0.8:
            queries.append(("apply_point", r.randrange(n), r.randint(-1000, 1000)))
        elif choice < 0.9:
            queries.append(("max_right", r.randrange(n + 1), r.randint(-2000, 2000)))
        else:
            queries.append(("min_left", r.randrange(n + 1), r.randint(-2000, 2000)))
    return values, queries


def run_lazysegtree(values, queries):
    inf = float("inf")
    seg = lazysegtree_mod.lazy_segtree(
        list(values), min, inf, lambda f, x: f + x, lambda f, g: f + g, 0
    )
    for q in queries:
        op = q[0]
        if op == "apply":
            seg.apply(q[1], q[2], q[3])
        elif op == "prod":
            seg.prod(q[1], q[2])
        elif op == "set":
            seg.set(q[1], q[2])
        elif op == "get":
            seg.get(q[1])
        elif op == "all_prod":
            seg.all_prod()
        elif op == "apply_point":
            seg.apply_point(q[1], q[2])
        elif op == "max_right":
            threshold = q[2]
            # min is non-increasing as the range grows, so "value >= threshold"
            # is a valid (monotonically falling) predicate for max_right/min_left.
            seg.max_right(q[1], lambda x, th=threshold: x >= th)
        else:
            threshold = q[2]
            seg.min_left(q[1], lambda x, th=threshold: x >= th)
    return seg


# ---------------------------------------------------------------------------
# dsu: leader / merge / same / size / groups on a large number of elements
# ---------------------------------------------------------------------------
def build_dsu_workload():
    r = _rng(3)
    n = 300_000
    merge_ops = [(r.randrange(n), r.randrange(n)) for _ in range(n)]
    leader_queries = [r.randrange(n) for _ in range(n)]
    same_queries = [(r.randrange(n), r.randrange(n)) for _ in range(n)]
    size_queries = [r.randrange(n) for _ in range(n)]
    return n, merge_ops, leader_queries, same_queries, size_queries


def run_dsu(n, merge_ops, leader_queries, same_queries, size_queries):
    d = dsu_mod.dsu(n)
    for a, b in merge_ops:
        d.merge(a, b)
    for a in leader_queries:
        d.leader(a)
    for a, b in same_queries:
        d.same(a, b)
    for a in size_queries:
        d.size(a)
    d.groups()
    return d


# ---------------------------------------------------------------------------
# maxflow: add_edge / get_edge / edges / change_edge / flow / min_cut on a
# random DAG (Dinic's algorithm)
# ---------------------------------------------------------------------------
def build_maxflow_workload():
    r = _rng(4)
    n, m = 50_000, 200_000
    edges = []
    for _ in range(m):
        u = r.randrange(n - 1)
        v = r.randrange(u + 1, n)
        edges.append((u, v, r.randint(1, 1000)))
    return n, edges


def run_maxflow(n, edges):
    g = maxflow_mod.mf_graph(n)
    for u, v, cap in edges:
        g.add_edge(u, v, cap)
    g.get_edge(0)
    g.edges()
    g.change_edge(0, 2000, 500)
    g.flow(0, n - 1)
    g.min_cut(0)
    return g


# ---------------------------------------------------------------------------
# mincostflow: add_edge / get_edge / edges / slope / flow on a random DAG
# (successive shortest paths)
# ---------------------------------------------------------------------------
def build_mincostflow_workload():
    r = _rng(5)
    n, m = 5_000, 25_000
    edges = []
    for _ in range(m):
        u = r.randrange(n - 1)
        v = r.randrange(u + 1, n)
        edges.append((u, v, r.randint(1, 20), r.randint(1, 100)))
    return n, edges


def run_mincostflow(n, edges):
    g = mincostflow_mod.mcf_graph(n)
    for u, v, cap, cost in edges:
        g.add_edge(u, v, cap, cost)
    g.slope(0, n - 1)
    g.get_edge(0)
    g.edges()
    g.flow(0, n - 1)
    return g


# ---------------------------------------------------------------------------
# convolution: NTT-based convolution of two large arrays
# ---------------------------------------------------------------------------
def build_convolution_workload():
    r = _rng(6)
    n = 1 << 16
    a = [r.randrange(MOD) for _ in range(n)]
    b = [r.randrange(MOD) for _ in range(n)]
    return a, b


def run_convolution(a, b):
    fft = convolution_mod.FFT(MOD)
    return fft.convolution(a, b)


# A long array against a short one. This is the other cost regime of
# convolution (and a common one in practice), so it is benchmarked separately
# from the balanced case above.
def build_convolution_lopsided_workload():
    r = _rng(14)
    a = [r.randrange(MOD) for _ in range(1 << 16)]
    b = [r.randrange(MOD) for _ in range(256)]
    return a, b


def run_convolution_lopsided(a, b):
    fft = convolution_mod.FFT(MOD)
    return fft.convolution(a, b)


# ---------------------------------------------------------------------------
# scc: Tarjan's algorithm on a large random directed graph
# ---------------------------------------------------------------------------
def build_scc_workload():
    r = _rng(7)
    n, m = 120_000, 360_000
    edges = [(r.randrange(n), r.randrange(n)) for _ in range(m)]
    return n, edges


def run_scc(n, edges):
    return scc_mod.scc(n, edges)


# ---------------------------------------------------------------------------
# fps: formal power series ops (exp/log/diff/integral/add/sub) on a large
# random series
# ---------------------------------------------------------------------------
def build_fps_workload():
    r = _rng(8)
    n = 8_192
    seq = [0] + [r.randrange(MOD) for _ in range(n - 1)]
    return (seq,)


def run_fps(seq):
    a = fps_mod.FPS(seq)
    b = a.exp()
    c = b.log()
    d = c.diff()
    e = d.integral()
    g = (b + a) - a
    return c.resize(len(seq)), e, g


# ---------------------------------------------------------------------------
# fenwicktree: add / sum on a large array
# ---------------------------------------------------------------------------
def build_fenwicktree_workload():
    r = _rng(9)
    n, q = 300_000, 300_000
    add_ops = [(r.randrange(n), r.randint(-1000, 1000)) for _ in range(q)]
    sum_ops = []
    for _ in range(q):
        l = r.randrange(n)
        rr = r.randrange(l, n + 1)
        sum_ops.append((l, rr))
    return n, add_ops, sum_ops


def run_fenwicktree(n, add_ops, sum_ops):
    ft = fenwicktree_mod.fenwick_tree(n)
    for p, x in add_ops:
        ft.add(p, x)
    for l, rr in sum_ops:
        ft.sum(l, rr)
    return ft


# ---------------------------------------------------------------------------
# acl_math: inv_gcd / inv_mod / crt / floor_sum on a large batch of random
# queries
# ---------------------------------------------------------------------------
_CRT_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
_MOD_BIG = (1 << 61) - 1


def build_acl_math_workload():
    r = _rng(10)
    q = 100_000
    inv_mod_queries = [r.randrange(1, _MOD_BIG) for _ in range(q)]
    inv_gcd_queries = [(r.randrange(1, 10**9), r.randint(1, 10**9)) for _ in range(q)]
    crt_queries = [[r.randrange(p) for p in _CRT_PRIMES] for _ in range(q)]
    floor_sum_queries = [
        (
            r.randint(1, 10**6),
            r.randint(1, 10**6),
            r.randint(0, 10**6),
            r.randint(0, 10**6),
        )
        for _ in range(q)
    ]
    return inv_mod_queries, inv_gcd_queries, crt_queries, floor_sum_queries


def run_acl_math(inv_mod_queries, inv_gcd_queries, crt_queries, floor_sum_queries):
    for x in inv_mod_queries:
        acl_math_mod.inv_mod(x, _MOD_BIG)
    for a, b in inv_gcd_queries:
        acl_math_mod.inv_gcd(a, b)
    for rems in crt_queries:
        acl_math_mod.crt(rems, list(_CRT_PRIMES))
    for n, m, a, b in floor_sum_queries:
        acl_math_mod.floor_sum(n, m, a, b)


# ---------------------------------------------------------------------------
# acl_string: suffix_array / lcp_array / z_algorithm on a large random string
# ---------------------------------------------------------------------------
def build_acl_string_workload():
    r = _rng(11)
    n = 100_000
    s = "".join(r.choice("abcd") for _ in range(n))
    return (s,)


def run_acl_string(s):
    st = acl_string_mod.String(s)
    sa = st.suffix_array()
    lcp = st.lcp_array(sa)
    z = st.z_algorithm()
    len(st)
    st[0]
    str(st)
    repr(st)
    return sa, lcp, z


# ---------------------------------------------------------------------------
# prime_fact: is_probable_prime / prime_fact / divisors / totient / lcm on a
# large batch of random numbers
# ---------------------------------------------------------------------------
def build_prime_fact_workload():
    r = _rng(12)
    is_prime_queries = [r.randrange(2, 10**7) for _ in range(20_000)]
    fact_queries = [r.randrange(2, 10**7) for _ in range(2_000)]
    lcm_queries = [(r.randrange(1, 10**6), r.randrange(1, 10**6)) for _ in range(2_000)]
    return is_prime_queries, fact_queries, lcm_queries


def run_prime_fact(is_prime_queries, fact_queries, lcm_queries):
    for n in is_prime_queries:
        prime_fact_mod.is_probable_prime(n)
    for n in fact_queries:
        prime_fact_mod.prime_fact(n)
        prime_fact_mod.divisors(n)
        prime_fact_mod.totient(n)
    for x, y in lcm_queries:
        prime_fact_mod.lcm(x, y)


# ---------------------------------------------------------------------------
# two_sat: a large random 2-SAT instance
# ---------------------------------------------------------------------------
def build_two_sat_workload():
    r = _rng(13)
    n, m = 200_000, 400_000
    clause = [
        (
            r.randrange(n),
            r.choice([True, False]),
            r.randrange(n),
            r.choice([True, False]),
        )
        for _ in range(m)
    ]
    return n, clause


def run_two_sat(n, clause):
    return two_sat_mod.two_sat(n, clause)


BENCHMARKS = [
    ("segtree", build_segtree_workload, run_segtree),
    ("lazysegtree", build_lazysegtree_workload, run_lazysegtree),
    ("dsu", build_dsu_workload, run_dsu),
    ("maxflow", build_maxflow_workload, run_maxflow),
    ("mincostflow", build_mincostflow_workload, run_mincostflow),
    ("convolution", build_convolution_workload, run_convolution),
    (
        "convolution_lopsided",
        build_convolution_lopsided_workload,
        run_convolution_lopsided,
    ),
    ("scc", build_scc_workload, run_scc),
    ("fps", build_fps_workload, run_fps),
    ("fenwicktree", build_fenwicktree_workload, run_fenwicktree),
    ("acl_math", build_acl_math_workload, run_acl_math),
    ("acl_string", build_acl_string_workload, run_acl_string),
    ("prime_fact", build_prime_fact_workload, run_prime_fact),
    ("two_sat", build_two_sat_workload, run_two_sat),
]
