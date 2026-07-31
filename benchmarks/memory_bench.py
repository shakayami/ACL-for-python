#!/usr/bin/env python3
"""Measure peak memory usage (via tracemalloc) for ACL-python, using the same
Library-Checker-calibrated workloads as benchmarks/test_time.py.

Usage:
    python benchmarks/memory_bench.py --output result.json

Unlike wall-clock time, tracemalloc's peak is deterministic for a fixed input,
so a single pass is enough and the comparison needs no noise allowance.

Honours ACL_BENCH_SCALE and ACL_BENCH_ONLY exactly as benchmarks/test_time.py
does, so a pull request measures the same subset for time and for memory.
"""

import argparse
import json
import os
import sys
import tracemalloc

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import workloads  # noqa: E402


def measure(workload):
    args = workload.build()
    tracemalloc.start()
    before, _ = tracemalloc.get_traced_memory()
    result = workload.run(*args)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del result
    return peak - before


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    results = []
    for workload in workloads.SELECTED:
        peak_bytes = measure(workload)
        results.append(
            {
                "name": workload.name,
                "peak_bytes": peak_bytes,
                "module": workload.module,
                "problem": workload.problem or "",
            }
        )
        print(f"{workload.name}: {peak_bytes / 1024:.1f} KiB", flush=True)

    with open(args.output, "w") as f:
        json.dump(
            {"scale": workloads.SCALE, "benchmarks": results},
            f,
            indent=2,
        )


if __name__ == "__main__":
    main()
