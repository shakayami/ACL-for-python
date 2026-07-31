"""Benchmark workloads, calibrated against Library Checker problems.

Why this file looks the way it does
-----------------------------------
The point of these benchmarks is to predict whether a change makes a real
submission faster.  A synthetic workload that exercises "every public method
with a made-up query mix" does not do that: it can report a large win for an
optimisation that a real judge run barely notices (or that is actually a
regression), because the operation mix, the operand types and the input sizes
are all different from what the judge runs.

So every primary workload here is a transcription of an actual problem from
https://github.com/yosupo06/library-checker-problems :

* the input is generated the way that problem's ``gen/max_random.cpp`` does
  (same query mix, same value ranges, same ``uniform_pair`` range
  distribution),
* the sizes are that problem's maximum constraints (``full_size`` on each
  workload), scaled by ``ACL_BENCH_SCALE`` so CI stays affordable,
* the ``run`` function is shaped like an accepted submission: it uses the same
  monoid / operator the submission would use, and it accumulates the answers
  instead of throwing them away.

That last point matters more than it looks.  ``segtree(values, max, -1)``
measures the segment tree with the cheapest possible ``op`` (a C builtin), so
Python-level overhead inside the tree dominates and any change to it looks
enormous.  Point Set Range Composite uses a Python lambda that composes affine
maps, which costs an order of magnitude more per call -- the same change is
then worth a few percent.  Benchmarking the first and shipping for the second
is exactly how a benchmark ends up disagreeing with the judge.

A handful of secondary workloads (``extra_*``, ``Workload.problem is None``)
cover public methods that no Library Checker problem exercises.  They exist as
a regression net only; their timings are *not* calibrated against anything and
should not be used to justify a performance claim.

Sizing
------
``ACL_BENCH_SCALE`` scales N/Q/M.  The query mix, operand types and range
distribution are scale-invariant, so a scaled run keeps the shape that makes
the benchmark predictive while running in a fraction of the time.

A single global scale is not enough on its own: at the same fraction of their
respective maxima, ``zalgorithm`` finishes in 20ms while ``bipartitematching``
takes three minutes, and a workload that runs for 20ms measures the timer more
than it measures the library.  So each workload also carries a ``COST_FACTOR``
that normalises for its per-element cost.  The effective fraction is
``min(1, ACL_BENCH_SCALE * COST_FACTOR[name])`` -- capped, so no workload ever
runs past the constraints the judge actually enforces.

* ``ACL_BENCH_SCALE`` unset (default 0.2): every workload takes roughly one to
  four seconds per round.
* ``ACL_BENCH_SCALE=max``: every workload at its exact Library Checker maximum.
  Expect this to take well over an hour in CPython.
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
INF = 1 << 62

LIBRARY_CHECKER = "https://judge.yosupo.jp/problem/"


DEFAULT_SCALE = 0.2

# Per-workload cost normalisation; see "Sizing" above. A factor of 5 means the
# workload reaches its Library Checker maximum already at the default scale
# (it is cheap enough that there is no reason to shrink it); a factor below 1
# means the module is too slow for CPython to reach the judge's constraints in
# a CI-sized budget. Values were picked so every workload lands in the same
# one-to-four-second band at the default scale -- re-measure before changing
# one, and change it only for time budget, never to flatter a result.
COST_FACTOR = {
    "point_add_range_sum": 3.0,
    "staticrmq": 3.0,
    "point_set_range_composite": 2.0,
    "range_affine_range_sum": 0.5,
    "unionfind": 5.0,
    "scc": 5.0,
    "two_sat": 3.0,
    # mf_graph.flow runs a full BFS per augmenting path rather than per phase,
    # so unit-capacity matching costs O(V*E*flow): 196s at 20% of the judge's
    # size. This factor keeps CI affordable; it is not a claim that the size is
    # representative.
    "bipartitematching": 0.15,
    "assignment": 2.5,
    "convolution_mod": 1.0,
    "inv_of_formal_power_series": 1.0,
    "log_of_formal_power_series": 0.5,
    "exp_of_formal_power_series": 0.5,
    "suffixarray": 5.0,
    "zalgorithm": 5.0,
    "number_of_substrings": 5.0,
    "sum_of_floor_of_linear": 5.0,
    "primality_test": 5.0,
    "factorize": 5.0,
    # The extras have no judge constraints to cap them against, so their
    # "maximum" is just a size chosen to keep each one measurable (a workload
    # that finishes in 20ms measures the timer, not the library).
    "extra_segtree_binary_search": 1.0,
    "extra_dsu_groups": 5.0,
    "extra_maxflow_edges": 5.0,
    "extra_mincostflow_slope": 5.0,
    "extra_acl_math_crt": 5.0,
    "extra_prime_fact_divisors": 1.0,
}


def _env_scale():
    raw = os.environ.get("ACL_BENCH_SCALE", "").strip().lower()
    if not raw:
        return DEFAULT_SCALE
    if raw in ("max", "full"):
        # Every factor is <= 5, so this pins every workload to its cap.
        return float("inf")
    try:
        value = float(raw)
    except ValueError:
        raise ValueError(
            f"ACL_BENCH_SCALE must be a positive float or 'max', got {raw!r}"
        )
    if value <= 0:
        raise ValueError(f"ACL_BENCH_SCALE must be positive, got {value}")
    return value


SCALE = _env_scale()


def effective_scale(name):
    """Fraction of the Library Checker maximum this workload actually runs at."""
    return min(1.0, SCALE * COST_FACTOR[name])


def _scaled(n, name, minimum=1):
    """Scale a Library Checker constraint down for CI."""
    return max(minimum, int(n * effective_scale(name)))


def _rng(seed):
    return random.Random(seed)


def _uniform_pair(rnd, lower, upper):
    """Port of library-checker-problems' ``Random::uniform_pair``.

    Picks two distinct values from the *inclusive* range [lower, upper] and
    returns them sorted, i.e. a non-empty subinterval [l, r) of [lower, upper).
    This is not the same distribution as ``l = randrange(n); r = randrange(l,
    n + 1)``: uniform_pair is symmetric in l and produces a mean width of
    roughly n/3, which is what the judge's segment-tree queries actually cost.
    """
    while True:
        a = rnd.randint(lower, upper)
        b = rnd.randint(lower, upper)
        if a != b:
            return (a, b) if a < b else (b, a)


class Workload:
    """One benchmark: a Library Checker problem, or an uncalibrated extra."""

    def __init__(self, name, module, build, run, full_size, problem=None, note=""):
        self.name = name
        self.module = module
        self.build = build
        self.run = run
        self.full_size = full_size
        self.problem = problem  # Library Checker slug, or None for extras
        self.note = note

    @property
    def url(self):
        return LIBRARY_CHECKER + self.problem if self.problem else None

    @property
    def effective_scale(self):
        """Fraction of ``full_size`` this run actually uses."""
        return effective_scale(self.name)

    def __iter__(self):
        # Kept so existing `for name, build_fn, run_fn in BENCHMARKS` consumers
        # keep working.
        return iter((self.name, self.build, self.run))


# ===========================================================================
# data_structure/point_add_range_sum  --  fenwicktree
# ===========================================================================
def build_point_add_range_sum():
    r = _rng(1)
    n = q = _scaled(500_000, "point_add_range_sum")
    a_max = 1_000_000_000
    a = [r.randint(0, a_max) for _ in range(n)]
    queries = []
    for _ in range(q):
        if r.randint(0, 1) == 0:
            queries.append((0, r.randint(0, n - 1), r.randint(0, a_max)))
        else:
            queries.append((1,) + _uniform_pair(r, 0, n))
    return n, a, queries


def run_point_add_range_sum(n, a, queries):
    ft = fenwicktree_mod.fenwick_tree(n)
    for i in range(n):
        ft.add(i, a[i])
    answer = 0
    for t, x, y in queries:
        if t == 0:
            ft.add(x, y)
        else:
            answer += ft.sum(x, y)
    return answer


# ===========================================================================
# data_structure/staticrmq  --  segtree with a C-level op
# ===========================================================================
def build_staticrmq():
    r = _rng(2)
    n = q = _scaled(500_000, "staticrmq")
    a = [r.randint(0, 1_000_000_000) for _ in range(n)]
    queries = [_uniform_pair(r, 0, n) for _ in range(q)]
    return a, queries


def run_staticrmq(a, queries):
    seg = segtree_mod.segtree(a, min, INF)
    answer = 0
    for l, rr in queries:
        answer ^= seg.prod(l, rr)
    return answer


# ===========================================================================
# data_structure/point_set_range_composite  --  segtree with a Python op
# ===========================================================================
def build_point_set_range_composite():
    r = _rng(3)
    n = q = _scaled(500_000, "point_set_range_composite")
    f = [(r.randint(1, MOD - 1), r.randint(0, MOD - 1)) for _ in range(n)]
    queries = []
    for _ in range(q):
        if r.randint(0, 1) == 0:
            queries.append(
                (0, r.randint(0, n - 1), r.randint(1, MOD - 1), r.randint(0, MOD - 1))
            )
        else:
            l, rr = _uniform_pair(r, 0, n)
            queries.append((1, l, rr, r.randint(0, MOD - 1)))
    return f, queries


def _compose(f, g):
    # g after f: (g.a * f.a) x + (g.a * f.b + g.b)
    return (f[0] * g[0] % MOD, (g[0] * f[1] + g[1]) % MOD)


def run_point_set_range_composite(f, queries):
    seg = segtree_mod.segtree(list(f), _compose, (1, 0))
    answer = 0
    for query in queries:
        if query[0] == 0:
            _, p, c, d = query
            seg.set(p, (c, d))
        else:
            _, l, rr, x = query
            a, b = seg.prod(l, rr)
            answer += (a * x + b) % MOD
    return answer


# ===========================================================================
# data_structure/range_affine_range_sum  --  lazysegtree
# ===========================================================================
def build_range_affine_range_sum():
    r = _rng(4)
    n = q = _scaled(500_000, "range_affine_range_sum")
    a = [r.randint(0, MOD - 1) for _ in range(n)]
    queries = []
    for _ in range(q):
        l, rr = _uniform_pair(r, 0, n)
        if r.randint(0, 1) == 0:
            queries.append((0, l, rr, r.randint(1, MOD - 1), r.randint(0, MOD - 1)))
        else:
            queries.append((1, l, rr, 0, 0))
    return a, queries


def _raras_op(x, y):
    return ((x[0] + y[0]) % MOD, x[1] + y[1])


def _raras_mapping(f, x):
    return ((f[0] * x[0] + f[1] * x[1]) % MOD, x[1])


def _raras_composition(f, g):
    # f after g
    return (f[0] * g[0] % MOD, (f[0] * g[1] + f[1]) % MOD)


def run_range_affine_range_sum(a, queries):
    seg = lazysegtree_mod.lazy_segtree(
        [(v, 1) for v in a],
        _raras_op,
        (0, 0),
        _raras_mapping,
        _raras_composition,
        (1, 0),
    )
    answer = 0
    for t, l, rr, b, c in queries:
        if t == 0:
            seg.apply(l, rr, (b, c))
        else:
            answer += seg.prod(l, rr)[0]
    return answer


# ===========================================================================
# data_structure/unionfind  --  dsu
# ===========================================================================
def build_unionfind():
    r = _rng(5)
    n = _scaled(200_000, "unionfind")
    q = _scaled(200_000, "unionfind")
    queries = [
        (r.randint(0, 1), r.randint(0, n - 1), r.randint(0, n - 1)) for _ in range(q)
    ]
    return n, queries


def run_unionfind(n, queries):
    d = dsu_mod.dsu(n)
    answer = 0
    for t, u, v in queries:
        if t == 0:
            d.merge(u, v)
        else:
            answer += d.same(u, v)
    return answer


# ===========================================================================
# graph/scc  --  scc
# ===========================================================================
def build_scc():
    r = _rng(6)
    n = _scaled(500_000, "scc")
    m = _scaled(500_000, "scc")
    edges = [(r.randint(0, n - 1), r.randint(0, n - 1)) for _ in range(m)]
    return n, edges


def run_scc(n, edges):
    groups = scc_mod.scc(n, edges)
    return len(groups)


# ===========================================================================
# other/two_sat  --  two_sat
# ===========================================================================
def build_two_sat():
    r = _rng(7)
    n = _scaled(500_000, "two_sat")
    m = _scaled(500_000, "two_sat")
    clause = []
    for _ in range(m):
        i = r.randint(0, n - 1)
        j = r.randint(0, n - 1)
        clause.append((i, r.randint(0, 1) == 1, j, r.randint(0, 1) == 1))
    return n, clause


def run_two_sat(n, clause):
    answer = two_sat_mod.two_sat(n, clause)
    if answer is None:  # UNSATISFIABLE
        return -1
    return sum(answer)


# ===========================================================================
# graph/bipartitematching  --  maxflow (Dinic)
# ===========================================================================
def build_bipartitematching():
    r = _rng(8)
    left = _scaled(100_000, "bipartitematching")
    right = _scaled(100_000, "bipartitematching")
    m = _scaled(200_000, "bipartitematching")
    # The generator inserts into a std::set, so duplicate edges collapse.
    edges = {(r.randint(0, left - 1), r.randint(0, right - 1)) for _ in range(m)}
    return left, right, sorted(edges)


def run_bipartitematching(left, right, edges):
    s = left + right
    t = s + 1
    g = maxflow_mod.mf_graph(t + 1)
    for i in range(left):
        g.add_edge(s, i, 1)
    for j in range(right):
        g.add_edge(left + j, t, 1)
    for u, v in edges:
        g.add_edge(u, left + v, 1)
    return g.flow(s, t)


# ===========================================================================
# graph/assignment  --  mincostflow (successive shortest paths)
# ===========================================================================
def build_assignment():
    r = _rng(9)
    n = _scaled(500, "assignment")
    a_abs_max = 1_000_000_000
    a = [[r.randint(-a_abs_max, a_abs_max) for _ in range(n)] for _ in range(n)]
    return n, a


def run_assignment(n, a):
    # mcf_graph needs non-negative costs, so shift by the constraint bound the
    # way a real submission does and subtract the shift back out at the end.
    shift = 1_000_000_000
    s = 2 * n
    t = s + 1
    g = mincostflow_mod.mcf_graph(t + 1)
    for i in range(n):
        g.add_edge(s, i, 1, 0)
        g.add_edge(n + i, t, 1, 0)
    for i in range(n):
        row = a[i]
        for j in range(n):
            g.add_edge(i, n + j, 1, row[j] + shift)
    flow, cost = g.flow(s, t)
    return cost - flow * shift


# ===========================================================================
# convolution/convolution_mod  --  convolution (NTT)
# ===========================================================================
def build_convolution_mod():
    r = _rng(10)
    n = _scaled(524_288, "convolution_mod")
    m = _scaled(524_288, "convolution_mod")
    a = [r.randint(0, MOD - 1) for _ in range(n)]
    b = [r.randint(0, MOD - 1) for _ in range(m)]
    return a, b


def run_convolution_mod(a, b):
    fft = convolution_mod.FFT(MOD)
    c = fft.convolution(a, b)
    return c[0] ^ c[-1]


# ===========================================================================
# polynomial/{inv,log,exp}_of_formal_power_series  --  fps
# ===========================================================================
def build_inv_of_formal_power_series():
    r = _rng(11)
    n = _scaled(500_000, "inv_of_formal_power_series")
    return ([r.randint(1, MOD - 1)] + [r.randint(0, MOD - 1) for _ in range(n - 1)],)


def run_inv_of_formal_power_series(a):
    return fps_mod.FPS(a).inv(len(a)).Func[-1]


def build_log_of_formal_power_series():
    r = _rng(12)
    n = _scaled(500_000, "log_of_formal_power_series")
    return ([1] + [r.randint(0, MOD - 1) for _ in range(n - 1)],)


def run_log_of_formal_power_series(a):
    return fps_mod.FPS(a).log().resize(len(a)).Func[-1]


def build_exp_of_formal_power_series():
    r = _rng(13)
    n = _scaled(500_000, "exp_of_formal_power_series")
    return ([0] + [r.randint(0, MOD - 1) for _ in range(n - 1)],)


def run_exp_of_formal_power_series(a):
    return fps_mod.FPS(a).exp(len(a)).Func[-1]


# ===========================================================================
# string/{suffixarray,zalgorithm,number_of_substrings}  --  acl_string
# ===========================================================================
_LOWER = "abcdefghijklmnopqrstuvwxyz"


def build_suffixarray():
    r = _rng(14)
    n = _scaled(500_000, "suffixarray")
    return ("".join(r.choice(_LOWER) for _ in range(n)),)


def run_suffixarray(s):
    sa = acl_string_mod.String(s).suffix_array()
    return sa[0] ^ sa[-1]


def build_zalgorithm():
    r = _rng(15)
    n = _scaled(500_000, "zalgorithm")
    return ("".join(r.choice(_LOWER) for _ in range(n)),)


def run_zalgorithm(s):
    return sum(acl_string_mod.String(s).z_algorithm())


def build_number_of_substrings():
    r = _rng(16)
    n = _scaled(500_000, "number_of_substrings")
    return ("".join(r.choice(_LOWER) for _ in range(n)),)


def run_number_of_substrings(s):
    st = acl_string_mod.String(s)
    n = len(s)
    sa = st.suffix_array()
    return n * (n + 1) // 2 - sum(st.lcp_array(sa))


# ===========================================================================
# number_theory/sum_of_floor_of_linear  --  acl_math.floor_sum
# ===========================================================================
def build_sum_of_floor_of_linear():
    r = _rng(17)
    t = _scaled(100_000, "sum_of_floor_of_linear")
    cases = []
    for _ in range(t):
        n = r.randint(1, 10**9)
        m = r.randint(1, 10**9)
        cases.append((n, m, r.randint(0, m - 1), r.randint(0, m - 1)))
    return (cases,)


def run_sum_of_floor_of_linear(cases):
    answer = 0
    for n, m, a, b in cases:
        answer += acl_math_mod.floor_sum(n, m, a, b)
    return answer


# ===========================================================================
# number_theory/primality_test  --  prime_fact.is_probable_prime
# ===========================================================================
def build_primality_test():
    r = _rng(18)
    q = _scaled(100_000, "primality_test")
    return ([r.randint(1, 10**18) for _ in range(q)],)


def run_primality_test(values):
    is_probable_prime = prime_fact_mod.is_probable_prime
    return sum(1 for n in values if is_probable_prime(n))


# ===========================================================================
# number_theory/factorize  --  prime_fact.prime_fact (Pollard's rho)
# ===========================================================================
def build_factorize():
    # gen/max.cpp emits consecutive integers just below 10^18; those are the
    # timing-relevant cases, far harder than uniformly random ones.
    q = _scaled(100, "factorize")
    return ([10**18 - i for i in range(q)],)


def run_factorize(values):
    answer = 0
    for n in values:
        answer += sum(prime_fact_mod.prime_fact(n).values())
    return answer


# ===========================================================================
# Extras: public methods no Library Checker problem exercises.
# Regression net only -- these timings predict nothing about judge runtime.
# ===========================================================================
def build_extra_segtree_binary_search():
    r = _rng(101)
    n = _scaled(200_000, "extra_segtree_binary_search")
    q = _scaled(200_000, "extra_segtree_binary_search")
    # A prefix-sum monoid with a threshold drawn from the whole range of
    # attainable sums: "longest prefix summing to at most x" is the standard
    # use of max_right, and it forces a full O(log n) descent. A max-monoid
    # with an independently random threshold would fail the predicate on the
    # first element almost every time and measure nothing.
    a = [r.randint(1, 1000) for _ in range(n)]
    total = sum(a)
    queries = [
        (r.randint(0, 1), r.randint(0, n), r.randint(0, total)) for _ in range(q)
    ]
    return a, queries


def _add(x, y):
    return x + y


def run_extra_segtree_binary_search(a, queries):
    seg = segtree_mod.segtree(a, _add, 0)
    answer = 0
    for t, p, threshold in queries:
        if t == 0:
            answer += seg.max_right(p, lambda x, th=threshold: x <= th)
        else:
            answer += seg.min_left(p, lambda x, th=threshold: x <= th)
    return answer


def build_extra_dsu_groups():
    r = _rng(102)
    n = _scaled(200_000, "extra_dsu_groups")
    merges = [(r.randint(0, n - 1), r.randint(0, n - 1)) for _ in range(n // 2)]
    sizes = [r.randint(0, n - 1) for _ in range(n)]
    return n, merges, sizes


def run_extra_dsu_groups(n, merges, sizes):
    d = dsu_mod.dsu(n)
    for a, b in merges:
        d.merge(a, b)
    answer = 0
    for a in sizes:
        answer += d.size(a)
    for a in sizes:
        answer ^= d.leader(a)
    return answer + len(d.groups())


def build_extra_maxflow_edges():
    r = _rng(103)
    n = _scaled(20_000, "extra_maxflow_edges")
    m = _scaled(60_000, "extra_maxflow_edges")
    edges = []
    for _ in range(m):
        u = r.randint(0, n - 2)
        v = r.randint(u + 1, n - 1)
        edges.append((u, v, r.randint(1, 1000)))
    return n, edges


def run_extra_maxflow_edges(n, edges):
    g = maxflow_mod.mf_graph(n)
    for u, v, cap in edges:
        g.add_edge(u, v, cap)
    g.change_edge(0, 2000, 500)
    g.get_edge(0)
    flow = g.flow(0, n - 1)
    return flow + len(g.edges()) + sum(g.min_cut(0))


def build_extra_mincostflow_slope():
    r = _rng(104)
    n = _scaled(2_000, "extra_mincostflow_slope")
    m = _scaled(8_000, "extra_mincostflow_slope")
    # In a purely random DAG the source has a handful of outgoing edges, so
    # slope() finishes after two augmentations and measures nothing. Fan out of
    # the source and into the sink so the successive-shortest-path loop runs.
    width = max(1, n // 10)
    edges = []
    for v in range(1, width + 1):
        edges.append((0, v, r.randint(1, 20), r.randint(1, 100)))
        edges.append((n - 1 - v, n - 1, r.randint(1, 20), r.randint(1, 100)))
    for _ in range(m):
        u = r.randint(1, n - 3)
        v = r.randint(u + 1, n - 2)
        edges.append((u, v, r.randint(1, 20), r.randint(1, 100)))
    return n, edges


def run_extra_mincostflow_slope(n, edges):
    g = mincostflow_mod.mcf_graph(n)
    for u, v, cap, cost in edges:
        g.add_edge(u, v, cap, cost)
    slope = g.slope(0, n - 1)
    g.get_edge(0)
    return len(slope) + len(g.edges())


_CRT_MODS = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
_MOD_BIG = (1 << 61) - 1


def build_extra_acl_math_crt():
    r = _rng(105)
    q = _scaled(100_000, "extra_acl_math_crt")
    inv_mod_queries = [r.randint(1, _MOD_BIG) for _ in range(q)]
    inv_gcd_queries = [(r.randint(1, 10**9), r.randint(1, 10**9)) for _ in range(q)]
    crt_queries = [[r.randrange(p) for p in _CRT_MODS] for _ in range(q // 10)]
    return inv_mod_queries, inv_gcd_queries, crt_queries


def run_extra_acl_math_crt(inv_mod_queries, inv_gcd_queries, crt_queries):
    answer = 0
    for x in inv_mod_queries:
        answer ^= acl_math_mod.inv_mod(x, _MOD_BIG)
    for a, b in inv_gcd_queries:
        answer ^= acl_math_mod.inv_gcd(a, b)[0]
    mods = list(_CRT_MODS)
    for rems in crt_queries:
        answer ^= acl_math_mod.crt(rems, mods)[0]
    return answer


def build_extra_prime_fact_divisors():
    r = _rng(106)
    values = [
        r.randint(2, 10**7)
        for _ in range(_scaled(10_000, "extra_prime_fact_divisors", minimum=100))
    ]
    lcm_queries = [
        (r.randint(1, 10**6), r.randint(1, 10**6))
        for _ in range(_scaled(10_000, "extra_prime_fact_divisors", minimum=100))
    ]
    return values, lcm_queries


def run_extra_prime_fact_divisors(values, lcm_queries):
    answer = 0
    for n in values:
        answer += len(prime_fact_mod.divisors(n))
        answer += prime_fact_mod.totient(n)
    for x, y in lcm_queries:
        answer ^= prime_fact_mod.lcm(x, y)
    return answer


# ===========================================================================
# Registry
# ===========================================================================
LIBRARY_CHECKER_BENCHMARKS = [
    Workload(
        "point_add_range_sum",
        "fenwicktree",
        build_point_add_range_sum,
        run_point_add_range_sum,
        "N = Q = 500,000",
        problem="point_add_range_sum",
    ),
    Workload(
        "staticrmq",
        "segtree",
        build_staticrmq,
        run_staticrmq,
        "N = Q = 500,000",
        problem="staticrmq",
        note="segtree with a C-level op (min); measures tree overhead",
    ),
    Workload(
        "point_set_range_composite",
        "segtree",
        build_point_set_range_composite,
        run_point_set_range_composite,
        "N = Q = 500,000",
        problem="point_set_range_composite",
        note="segtree with a Python-level op; measures op-dominated cost",
    ),
    Workload(
        "range_affine_range_sum",
        "lazysegtree",
        build_range_affine_range_sum,
        run_range_affine_range_sum,
        "N = Q = 500,000",
        problem="range_affine_range_sum",
    ),
    Workload(
        "unionfind",
        "dsu",
        build_unionfind,
        run_unionfind,
        "N = Q = 200,000",
        problem="unionfind",
    ),
    Workload(
        "scc",
        "scc",
        build_scc,
        run_scc,
        "N = M = 500,000",
        problem="scc",
    ),
    Workload(
        "two_sat",
        "two_sat",
        build_two_sat,
        run_two_sat,
        "N = M = 500,000",
        problem="two_sat",
    ),
    Workload(
        "bipartitematching",
        "maxflow",
        build_bipartitematching,
        run_bipartitematching,
        "L = R = 100,000, M = 200,000",
        problem="bipartitematching",
    ),
    Workload(
        "assignment",
        "mincostflow",
        build_assignment,
        run_assignment,
        "N = 500",
        problem="assignment",
        note="O(N^3)-ish in CPython; ACL_BENCH_SCALE=1 is far past the judge's TL",
    ),
    Workload(
        "convolution_mod",
        "convolution",
        build_convolution_mod,
        run_convolution_mod,
        "N = M = 524,288",
        problem="convolution_mod",
    ),
    Workload(
        "inv_of_formal_power_series",
        "fps",
        build_inv_of_formal_power_series,
        run_inv_of_formal_power_series,
        "N = 500,000",
        problem="inv_of_formal_power_series",
    ),
    Workload(
        "log_of_formal_power_series",
        "fps",
        build_log_of_formal_power_series,
        run_log_of_formal_power_series,
        "N = 500,000",
        problem="log_of_formal_power_series",
    ),
    Workload(
        "exp_of_formal_power_series",
        "fps",
        build_exp_of_formal_power_series,
        run_exp_of_formal_power_series,
        "N = 500,000",
        problem="exp_of_formal_power_series",
    ),
    Workload(
        "suffixarray",
        "acl_string",
        build_suffixarray,
        run_suffixarray,
        "N = 500,000",
        problem="suffixarray",
    ),
    Workload(
        "zalgorithm",
        "acl_string",
        build_zalgorithm,
        run_zalgorithm,
        "N = 500,000",
        problem="zalgorithm",
    ),
    Workload(
        "number_of_substrings",
        "acl_string",
        build_number_of_substrings,
        run_number_of_substrings,
        "N = 500,000",
        problem="number_of_substrings",
    ),
    Workload(
        "sum_of_floor_of_linear",
        "acl_math",
        build_sum_of_floor_of_linear,
        run_sum_of_floor_of_linear,
        "T = 100,000",
        problem="sum_of_floor_of_linear",
    ),
    Workload(
        "primality_test",
        "prime_fact",
        build_primality_test,
        run_primality_test,
        "Q = 100,000, N <= 10^18",
        problem="primality_test",
    ),
    Workload(
        "factorize",
        "prime_fact",
        build_factorize,
        run_factorize,
        "Q = 100, A <= 10^18",
        problem="factorize",
    ),
]

EXTRA_BENCHMARKS = [
    Workload(
        "extra_segtree_binary_search",
        "segtree",
        build_extra_segtree_binary_search,
        run_extra_segtree_binary_search,
        "N = Q = 200,000",
        note="max_right / min_left",
    ),
    Workload(
        "extra_dsu_groups",
        "dsu",
        build_extra_dsu_groups,
        run_extra_dsu_groups,
        "N = 200,000",
        note="size / leader / groups",
    ),
    Workload(
        "extra_maxflow_edges",
        "maxflow",
        build_extra_maxflow_edges,
        run_extra_maxflow_edges,
        "N = 20,000, M = 60,000",
        note="get_edge / change_edge / edges / min_cut",
    ),
    Workload(
        "extra_mincostflow_slope",
        "mincostflow",
        build_extra_mincostflow_slope,
        run_extra_mincostflow_slope,
        "N = 2,000, M = 8,000",
        note="slope / get_edge / edges",
    ),
    Workload(
        "extra_acl_math_crt",
        "acl_math",
        build_extra_acl_math_crt,
        run_extra_acl_math_crt,
        "Q = 100,000",
        note="inv_mod / inv_gcd / crt",
    ),
    Workload(
        "extra_prime_fact_divisors",
        "prime_fact",
        build_extra_prime_fact_divisors,
        run_extra_prime_fact_divisors,
        "Q = 10,000",
        note="divisors / totient / lcm",
    ),
]

BENCHMARKS = LIBRARY_CHECKER_BENCHMARKS + EXTRA_BENCHMARKS

BY_NAME = {w.name: w for w in BENCHMARKS}
