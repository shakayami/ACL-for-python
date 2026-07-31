#!/usr/bin/env python3
"""Pick the benchmarks a change can actually affect.

Running all 25 workloads on both branches of every pull request costs far more
Actions time than it earns: a change to ``segtree.py`` cannot make ``factorize``
faster, so measuring ``factorize`` only adds runtime and another chance for
noise to produce a spurious row.

The mapping is exact rather than heuristic because the library modules are
standalone -- none of them imports another (they are meant to be pasted into a
submission), so a change to ``scc.py`` reaches exactly the workloads whose
module is ``scc``. Note that ``two_sat.py`` and ``fps.py`` carry their own
inlined copies of the SCC and NTT routines; editing ``scc.py`` or
``convolution.py`` genuinely does not affect them, and the selection reflects
that.

Usage:
    python benchmarks/select_workloads.py --changed-files changed.txt
    git diff --name-only origin/master... | python benchmarks/select_workloads.py
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import workloads  # noqa: E402

# Touching any of these invalidates the comparison itself (the workloads or the
# harness changed), so everything has to run.
RUN_EVERYTHING = frozenset(
    {
        "benchmarks/workloads.py",
        "benchmarks/test_time.py",
        "benchmarks/memory_bench.py",
        "benchmarks/select_workloads.py",
        ".github/workflows/benchmark.yml",
    }
)

# Every benchmarked module is a single top-level file named after itself.
MODULE_FILE = {f"{w.module}.py": w.module for w in workloads.BENCHMARKS}


def _normalise(path):
    path = path.strip()
    # Not lstrip("./"): that strips every leading "." and "/", turning
    # ".github/workflows/benchmark.yml" into "github/workflows/benchmark.yml".
    if path.startswith("./"):
        path = path[2:]
    return path


def select(changed_files):
    """Workload names to benchmark, in registry order."""
    changed = {_normalise(path) for path in changed_files if path.strip()}
    if changed & RUN_EVERYTHING:
        return [w.name for w in workloads.BENCHMARKS]
    modules = {MODULE_FILE[path] for path in changed if path in MODULE_FILE}
    if not modules:
        return []
    return [w.name for w in workloads.BENCHMARKS if w.module in modules]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--changed-files",
        help="file listing changed paths, one per line (default: stdin)",
    )
    parser.add_argument(
        "--format",
        choices=("names", "csv"),
        default="names",
        help="'names' prints one per line; 'csv' is the ACL_BENCH_ONLY format",
    )
    args = parser.parse_args()

    if args.changed_files:
        with open(args.changed_files) as f:
            changed = f.read().splitlines()
    else:
        changed = sys.stdin.read().splitlines()

    names = select(changed)
    if args.format == "csv":
        print(",".join(names))
    else:
        for name in names:
            print(name)


if __name__ == "__main__":
    main()
