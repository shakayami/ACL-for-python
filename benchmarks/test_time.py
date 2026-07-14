"""Execution-time benchmarks, run via pytest-benchmark.

Usage:
    pytest benchmarks/test_time.py --benchmark-json=result.json
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import workloads  # noqa: E402


@pytest.mark.parametrize("name,build_fn,run_fn", workloads.BENCHMARKS, ids=[b[0] for b in workloads.BENCHMARKS])
def test_benchmark(benchmark, name, build_fn, run_fn):
    args = build_fn()
    benchmark.pedantic(run_fn, args=args, rounds=3, warmup_rounds=1)
