#!/usr/bin/env python3
"""Measure peak memory usage (via tracemalloc) for ACL-python's core data
structures, using the same workloads as benchmarks/test_time.py.

Usage:
    python benchmarks/memory_bench.py --output result.json
"""

import argparse
import json
import os
import sys
import tracemalloc

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import workloads  # noqa: E402


def measure(build_fn, run_fn):
    args = build_fn()
    tracemalloc.start()
    before, _ = tracemalloc.get_traced_memory()
    result = run_fn(*args)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del result
    return peak - before


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    results = []
    for name, build_fn, run_fn in workloads.BENCHMARKS:
        peak_bytes = measure(build_fn, run_fn)
        results.append({"name": name, "peak_bytes": peak_bytes})
        print(f"{name}: {peak_bytes / 1024:.1f} KiB")

    with open(args.output, "w") as f:
        json.dump({"benchmarks": results}, f, indent=2)


if __name__ == "__main__":
    main()
