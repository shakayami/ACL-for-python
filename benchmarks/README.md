# Benchmarks

These benchmarks exist to answer one question: **will this change make a real
submission faster?**

Every primary workload is therefore a transcription of an actual problem from
[yosupo06/library-checker-problems](https://github.com/yosupo06/library-checker-problems).
If a change is faster here, it should be faster on
[Library Checker](https://judge.yosupo.jp/) too.

## Why the old workloads disagreed with the judge

The previous suite generated its own query mixes ("exercise every public
method"), which made its numbers systematically misleading:

| Problem | Effect |
|---|---|
| Invented query mix | 20% of the segtree benchmark was `max_right`/`min_left`, which Point Set Range Composite never calls. A 30% win in `prod` showed up as 8%; a win in a method nobody uses showed up as a headline number. |
| Unrealistic operators | `segtree(values, max, -1)` uses a C builtin as `op`, so tree-internal Python overhead dominated. Real submissions pass a Python lambda that costs an order of magnitude more per call, which dilutes the same change to a few percent. |
| Wrong range distribution | `l = randrange(n); r = randrange(l, n + 1)` is not the judge's `uniform_pair`, so query widths — and therefore segment-tree descent depth — were off. |
| Sizes below the constraints | segtree at 200k vs the judge's 500k, convolution at 2^16 vs 2^19, FPS at 8k vs 500k. |
| Results thrown away | `seg.prod(l, r)` with the return value discarded is not what a submission does. |
| `mean` of 3 rounds, compared across two sequential jobs | On a shared runner that is worth several percent on its own, and the report flagged ✅ at 1%. |

## What runs now

| Benchmark | Module | Library Checker problem | Max constraints |
|---|---|---|---|
| `point_add_range_sum` | `fenwicktree` | [Point Add Range Sum](https://judge.yosupo.jp/problem/point_add_range_sum) | N = Q = 500,000 |
| `staticrmq` | `segtree` | [Static RMQ](https://judge.yosupo.jp/problem/staticrmq) | N = Q = 500,000 |
| `point_set_range_composite` | `segtree` | [Point Set Range Composite](https://judge.yosupo.jp/problem/point_set_range_composite) | N = Q = 500,000 |
| `range_affine_range_sum` | `lazysegtree` | [Range Affine Range Sum](https://judge.yosupo.jp/problem/range_affine_range_sum) | N = Q = 500,000 |
| `unionfind` | `dsu` | [Unionfind](https://judge.yosupo.jp/problem/unionfind) | N = Q = 200,000 |
| `scc` | `scc` | [Strongly Connected Components](https://judge.yosupo.jp/problem/scc) | N = M = 500,000 |
| `two_sat` | `two_sat` | [2 SAT](https://judge.yosupo.jp/problem/two_sat) | N = M = 500,000 |
| `bipartitematching` | `maxflow` | [Matching on Bipartite Graph](https://judge.yosupo.jp/problem/bipartitematching) | L = R = 100,000, M = 200,000 |
| `assignment` | `mincostflow` | [Assignment Problem](https://judge.yosupo.jp/problem/assignment) | N = 500 |
| `convolution_mod` | `convolution` | [Convolution](https://judge.yosupo.jp/problem/convolution_mod) | N = M = 524,288 |
| `inv_of_formal_power_series` | `fps` | [Inv of FPS](https://judge.yosupo.jp/problem/inv_of_formal_power_series) | N = 500,000 |
| `log_of_formal_power_series` | `fps` | [Log of FPS](https://judge.yosupo.jp/problem/log_of_formal_power_series) | N = 500,000 |
| `exp_of_formal_power_series` | `fps` | [Exp of FPS](https://judge.yosupo.jp/problem/exp_of_formal_power_series) | N = 500,000 |
| `suffixarray` | `acl_string` | [Suffix Array](https://judge.yosupo.jp/problem/suffixarray) | N = 500,000 |
| `zalgorithm` | `acl_string` | [Z Algorithm](https://judge.yosupo.jp/problem/zalgorithm) | N = 500,000 |
| `number_of_substrings` | `acl_string` | [Number of Substrings](https://judge.yosupo.jp/problem/number_of_substrings) | N = 500,000 |
| `sum_of_floor_of_linear` | `acl_math` | [Sum of Floor of Linear](https://judge.yosupo.jp/problem/sum_of_floor_of_linear) | T = 100,000 |
| `primality_test` | `prime_fact` | [Primality Test](https://judge.yosupo.jp/problem/primality_test) | Q = 100,000, N ≤ 10^18 |
| `factorize` | `prime_fact` | [Factorize](https://judge.yosupo.jp/problem/factorize) | Q = 100, A ≤ 10^18 |

Inputs are generated the way each problem's `gen/max_random.cpp` does: same
query mix, same value ranges, and a faithful port of the judge's `uniform_pair`
for range queries. The `run_*` functions are shaped like accepted submissions —
same monoid, same operators, and they accumulate the answers rather than
discarding them. `tests/test_benchmark_workloads.py` checks each one against a
naive reference so a benchmark can never get "fast" by being wrong.

### API coverage workloads

`extra_*` workloads cover public methods no Library Checker problem exercises
(`max_right`/`min_left`, `dsu.groups`, `min_cut`, `change_edge`,
`mcf_graph.slope`, `crt`, `divisors`/`totient`/`lcm`). They are a regression
net only. **Their timings are not calibrated against anything — do not quote
them as speedups.** The report keeps them in a separate collapsed table for
that reason.

## Sizing

`ACL_BENCH_SCALE` scales N/Q/M. The query mix, operand types and range
distribution are scale-invariant, so a scaled run keeps the shape that makes
the benchmark predictive.

The modules differ by orders of magnitude in per-element cost, so each workload
also carries a `COST_FACTOR` in `workloads.py`. The effective size is
`min(1, ACL_BENCH_SCALE * COST_FACTOR[name])` of the judge's maximum — capped,
so a workload never runs past constraints the judge does not enforce.

```sh
# CI default: every workload lands in a one-to-four-second band
pytest benchmarks/test_time.py

# every workload at its exact Library Checker maximum (well over an hour)
ACL_BENCH_SCALE=max pytest benchmarks/test_time.py

# a single workload, at full size
ACL_BENCH_SCALE=max pytest benchmarks/test_time.py -k point_set_range_composite
```

Two workloads run well below the judge's constraints even at the default,
because the current implementations cannot reach them in CPython:

* `bipartitematching` (3% of L/R/M). `mf_graph.flow` runs a full BFS per
  augmenting path instead of per phase, so unit-capacity matching costs
  O(V·E·flow) rather than Dinic's O(E√V) — 196 seconds at 20% of the judge's
  size. The low factor is a CI budget decision, not a claim that the size is
  representative.
* `range_affine_range_sum`, `exp/log_of_formal_power_series` (10%).

## What runs, and when

Running all 25 workloads on both branches of every pull request costs far more
Actions time than it earns. So:

**On a pull request**, only the workloads whose module the diff touches are
measured. `select_workloads.py` maps changed files to workload names, and the
workflow passes them to both runners via `ACL_BENCH_ONLY`; `compare.py --only`
keeps the report to the same set rather than padding it with `n/a` rows. The
mapping is exact rather than heuristic, because none of the library modules
imports another — they are meant to be pasted into a submission — so a change
to `scc.py` reaches exactly the workloads whose module is `scc`.

Note that `two_sat.py` and `fps.py` carry their own inlined copies of the SCC
and NTT routines. Editing `scc.py` or `convolution.py` genuinely does not
affect them, and the selection reflects that; if you port an optimisation
between the copies, touch both files.

Changing `benchmarks/workloads.py`, `test_time.py`, `memory_bench.py`,
`select_workloads.py` or the workflow runs everything, because then the
comparison itself is what is in question. Changing anything else — docs, tests,
`compare.py` — runs nothing, and the PR comment says so.

```sh
git diff --name-only origin/master... | python benchmarks/select_workloads.py
ACL_BENCH_ONLY=staticrmq,unionfind pytest benchmarks/test_time.py
```

**On a schedule** (`benchmark-full.yml`, Mondays 03:00 UTC, or on demand via
*Run workflow*), the whole suite runs on master at `ACL_BENCH_SCALE=1.0` and is
compared against the previous sweep's artifact. That is the safety net for
drift that accumulates across many small PRs, and for anything the per-PR
selection cannot see. Results go to the job summary and are kept as artifacts
for 90 days.

## Reading the report

`compare.py` renders the PR comment. Two things about it are deliberate:

* **The statistic is the minimum, not the mean.** Interference from
  neighbouring jobs can only make a run slower, so the fastest observation is
  the closest estimate of the code's real cost. The mean mostly measures how
  busy the runner was.
* **A delta is only called a win or a regression when it exceeds the noise we
  actually measured** between passes, and never below 3%. Anything smaller is
  reported as `≈`. The base and PR branches are measured in *interleaved*
  passes for the same reason — running one to completion before the other turns
  the runner's drift into a fake delta.

Memory is measured with `tracemalloc` and is deterministic, so it needs only
one pass and a 1% allowance.

## Local use

```sh
pip install pytest pytest-benchmark

pytest benchmarks/test_time.py --benchmark-json=result.json
python benchmarks/memory_bench.py --output memory.json

python benchmarks/compare.py \
  --base-time base-time-*.json --pr-time pr-time-*.json \
  --base-memory base-memory.json --pr-memory pr-memory.json \
  --output report.md
```
