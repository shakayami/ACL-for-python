"""Deterministic workloads shared by the time (pytest-benchmark) and memory
(tracemalloc) benchmarks, so both measure exactly the same operations.
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

MOD = 998244353


def _rng(seed):
    return random.Random(seed)


# ---------------------------------------------------------------------------
# segtree: point-set / range-max on a large array
# ---------------------------------------------------------------------------
def build_segtree_workload():
    r = _rng(1)
    n, q = 50_000, 50_000
    values = [r.randint(1, 10**9) for _ in range(n)]
    queries = []
    for _ in range(q):
        if r.random() < 0.5:
            queries.append(("set", r.randrange(n), r.randint(1, 10**9)))
        else:
            l = r.randrange(n)
            queries.append(("prod", l, r.randrange(l, n + 1)))
    return values, queries


def run_segtree(values, queries):
    seg = segtree_mod.segtree(list(values), max, -1)
    for op, a, b in queries:
        if op == "set":
            seg.set(a, b)
        else:
            seg.prod(a, b)
    return seg


# ---------------------------------------------------------------------------
# lazysegtree: range-add / range-min
# ---------------------------------------------------------------------------
def build_lazysegtree_workload():
    r = _rng(2)
    n, q = 50_000, 50_000
    values = [0] * n
    queries = []
    for _ in range(q):
        l = r.randrange(n)
        rr = r.randrange(l, n + 1)
        if r.random() < 0.5:
            queries.append(("apply", l, rr, r.randint(-1000, 1000)))
        else:
            queries.append(("prod", l, rr))
    return values, queries


def run_lazysegtree(values, queries):
    inf = float("inf")
    seg = lazysegtree_mod.lazy_segtree(
        list(values), min, inf, lambda f, x: f + x, lambda f, g: f + g, 0
    )
    for q in queries:
        if q[0] == "apply":
            seg.apply(q[1], q[2], q[3])
        else:
            seg.prod(q[1], q[2])
    return seg


# ---------------------------------------------------------------------------
# dsu: merge / same on a large number of elements
# ---------------------------------------------------------------------------
def build_dsu_workload():
    r = _rng(3)
    n = 100_000
    ops = []
    for _ in range(n):
        ops.append(("merge", r.randrange(n), r.randrange(n)))
    for _ in range(n):
        ops.append(("same", r.randrange(n), r.randrange(n)))
    return n, ops


def run_dsu(n, ops):
    d = dsu_mod.dsu(n)
    for op, a, b in ops:
        if op == "merge":
            d.merge(a, b)
        else:
            d.same(a, b)
    return d


# ---------------------------------------------------------------------------
# maxflow: Dinic's algorithm on a random DAG
# ---------------------------------------------------------------------------
def build_maxflow_workload():
    r = _rng(4)
    n, m = 2_000, 8_000
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
    g.flow(0, n - 1)
    return g


# ---------------------------------------------------------------------------
# mincostflow: successive shortest paths on a smaller random DAG
# ---------------------------------------------------------------------------
def build_mincostflow_workload():
    r = _rng(5)
    n, m = 300, 1_500
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


# ---------------------------------------------------------------------------
# scc: Tarjan's algorithm on a large random directed graph
# ---------------------------------------------------------------------------
def build_scc_workload():
    r = _rng(7)
    n, m = 50_000, 150_000
    edges = [(r.randrange(n), r.randrange(n)) for _ in range(m)]
    return n, edges


def run_scc(n, edges):
    return scc_mod.scc(n, edges)


BENCHMARKS = [
    ("segtree", build_segtree_workload, run_segtree),
    ("lazysegtree", build_lazysegtree_workload, run_lazysegtree),
    ("dsu", build_dsu_workload, run_dsu),
    ("maxflow", build_maxflow_workload, run_maxflow),
    ("mincostflow", build_mincostflow_workload, run_mincostflow),
    ("convolution", build_convolution_workload, run_convolution),
    ("scc", build_scc_workload, run_scc),
]
