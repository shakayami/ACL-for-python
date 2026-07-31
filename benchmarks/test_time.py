"""Execution-time benchmarks, run via pytest-benchmark.

Usage:
    pytest benchmarks/test_time.py --benchmark-json=result.json

Environment:
    ACL_BENCH_SCALE   size of the workloads relative to the Library Checker
                      maximum constraints (see workloads.py). Default 0.2.
    ACL_BENCH_ROUNDS  timed rounds per workload per pass. Default 3.
    ACL_BENCH_ONLY    comma-separated workload names to run. Pull requests set
                      this to the modules they touch (see select_workloads.py).

The reported statistic that ``compare.py`` uses is the *minimum* across rounds
and across passes, not the mean: on a shared CI runner the mean is dominated by
interference from neighbouring jobs, and a 1-2% "improvement" in the mean is
almost always noise rather than a real change.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import workloads  # noqa: E402

ROUNDS = int(os.environ.get("ACL_BENCH_ROUNDS", "3"))


@pytest.mark.parametrize(
    "workload",
    workloads.SELECTED,
    ids=[w.name for w in workloads.SELECTED],
)
def test_benchmark(benchmark, workload):
    args = workload.build()
    benchmark.extra_info["module"] = workload.module
    benchmark.extra_info["problem"] = workload.problem or ""
    benchmark.extra_info["full_size"] = workload.full_size
    benchmark.extra_info["scale"] = workload.effective_scale
    # float("inf") is not portable through JSON, so send "max" as a string.
    benchmark.extra_info["global_scale"] = (
        "max" if workloads.SCALE == float("inf") else str(workloads.SCALE)
    )
    benchmark.extra_info["note"] = workload.note
    benchmark.pedantic(workload.run, args=args, rounds=ROUNDS, warmup_rounds=1)
