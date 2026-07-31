"""Tests for the benchmark comparison report.

The report is what people act on, so its thresholds need to hold: a real win
must be reported, and run-to-run noise must not be.
"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "benchmarks"
    ),
)

import compare  # noqa: E402


def write_time_json(path, samples, name="staticrmq", problem="staticrmq"):
    """One pytest-benchmark JSON file; ``samples`` maps name -> stats.min."""
    payload = {
        "benchmarks": [
            {
                "name": f"test_benchmark[{n}]",
                "stats": {"min": v, "mean": v * 1.2},
                "extra_info": {
                    "problem": problem if n == name else "",
                    "full_size": "N = Q = 500,000",
                    "scale": 0.6,
                    "global_scale": "0.2",
                    "note": "",
                },
            }
            for n, v in samples.items()
        ]
    }
    with open(path, "w") as f:
        json.dump(payload, f)


class TestNameParsing(unittest.TestCase):
    def test_parametrised_id(self):
        self.assertEqual(compare._benchmark_name("test_benchmark[scc]"), "scc")

    def test_plain_test_name(self):
        self.assertEqual(compare._benchmark_name("test_scc"), "scc")

    def test_unrecognised_name_passes_through(self):
        self.assertEqual(compare._benchmark_name("scc"), "scc")


class TestSpread(unittest.TestCase):
    def test_single_sample_has_no_measurable_noise(self):
        self.assertEqual(compare.spread([1.0]), 0.0)

    def test_relative_gap_between_best_and_worst(self):
        self.assertAlmostEqual(compare.spread([1.0, 1.5, 1.2]), 0.5)


class TestDeltaThresholds(unittest.TestCase):
    def test_real_improvement_is_flagged(self):
        self.assertIn("✅", compare.fmt_delta(1.0, 0.7, 0.03))

    def test_real_regression_is_flagged(self):
        self.assertIn("⚠️", compare.fmt_delta(1.0, 1.4, 0.03))

    def test_small_delta_is_not_flagged(self):
        out = compare.fmt_delta(1.0, 0.98, 0.03)
        self.assertIn("≈", out)
        self.assertNotIn("✅", out)

    def test_delta_below_measured_noise_is_not_flagged(self):
        # 10% faster, but the passes themselves varied by 20%.
        out = compare.fmt_delta(1.0, 0.90, 0.20)
        self.assertIn("≈", out)
        self.assertNotIn("✅", out)

    def test_identical_values_report_no_change(self):
        self.assertEqual(compare.fmt_delta(1.0, 1.0, 0.03), "0.0%")


class TestReport(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def path(self, name):
        return os.path.join(self.dir, name)

    def render(self, base_passes, pr_passes):
        base_files, pr_files = [], []
        for i, samples in enumerate(base_passes):
            p = self.path(f"base-{i}.json")
            write_time_json(p, samples)
            base_files.append(p)
        for i, samples in enumerate(pr_passes):
            p = self.path(f"pr-{i}.json")
            write_time_json(p, samples)
            pr_files.append(p)
        for p in ("base-mem.json", "pr-mem.json"):
            with open(self.path(p), "w") as f:
                json.dump({"benchmarks": []}, f)
        out = self.path("report.md")
        sys.argv = [
            "compare.py",
            "--base-time",
            *base_files,
            "--pr-time",
            *pr_files,
            "--base-memory",
            self.path("base-mem.json"),
            "--pr-memory",
            self.path("pr-mem.json"),
            "--output",
            out,
        ]
        with contextlib.redirect_stdout(io.StringIO()):
            compare.main()
        with open(out) as f:
            return f.read()

    @staticmethod
    def row(report, name):
        """The table row for one benchmark, so assertions never match the
        legend text (which itself mentions ✅ and ⚠️)."""
        for line in report.splitlines():
            if line.startswith("| ") and f"| {name} " in line.replace("[", "").replace(
                "]", " "
            ).replace("(https://judge.yosupo.jp/problem/", " ("):
                return line
        raise AssertionError(f"no row for {name!r} in:\n{report}")

    def test_minimum_is_taken_across_passes(self):
        # A single slow pass must not drag the reported time up.
        report = self.render(
            [{"staticrmq": 1.0}, {"staticrmq": 5.0}],
            [{"staticrmq": 1.0}, {"staticrmq": 1.0}],
        )
        self.assertIn("1.000s", report)
        self.assertNotIn("5.000s", report)

    def test_consistent_win_across_quiet_passes_is_flagged(self):
        report = self.render(
            [{"staticrmq": 1.00}, {"staticrmq": 1.01}],
            [{"staticrmq": 0.70}, {"staticrmq": 0.71}],
        )
        self.assertIn("✅", self.row(report, "staticrmq"))

    def test_win_smaller_than_the_noise_is_not_flagged(self):
        report = self.render(
            [{"staticrmq": 1.00}, {"staticrmq": 1.40}],
            [{"staticrmq": 0.92}, {"staticrmq": 1.30}],
        )
        row = self.row(report, "staticrmq")
        self.assertNotIn("✅", row)
        self.assertIn("≈", row)

    def test_extras_are_separated_from_calibrated_workloads(self):
        report = self.render(
            [{"staticrmq": 1.0, "extra_dsu_groups": 1.0}],
            [{"staticrmq": 1.0, "extra_dsu_groups": 1.0}],
        )
        self.assertIn("API coverage workloads", report)
        head, tail = report.split("API coverage workloads", 1)
        self.assertIn("staticrmq", head)
        self.assertIn("extra_dsu_groups", tail)

    def test_missing_side_renders_as_na(self):
        report = self.render([{}], [{"staticrmq": 1.0}])
        self.assertIn("| n/a |", report)

    def test_mismatched_scales_are_called_out(self):
        base = self.path("base-0.json")
        pr = self.path("pr-0.json")
        write_time_json(base, {"staticrmq": 1.0})
        write_time_json(pr, {"staticrmq": 1.0})
        with open(pr) as f:
            data = json.load(f)
        data["benchmarks"][0]["extra_info"]["global_scale"] = "1.0"
        with open(pr, "w") as f:
            json.dump(data, f)
        for p in ("base-mem.json", "pr-mem.json"):
            with open(self.path(p), "w") as f:
                json.dump({"benchmarks": []}, f)
        out = self.path("report.md")
        sys.argv = [
            "compare.py",
            "--base-time",
            base,
            "--pr-time",
            pr,
            "--base-memory",
            self.path("base-mem.json"),
            "--pr-memory",
            self.path("pr-mem.json"),
            "--output",
            out,
        ]
        with contextlib.redirect_stdout(io.StringIO()):
            compare.main()
        with open(out) as f:
            self.assertIn("different `ACL_BENCH_SCALE`", f.read())

    def test_problem_links_are_rendered(self):
        report = self.render([{"staticrmq": 1.0}], [{"staticrmq": 1.0}])
        self.assertIn("https://judge.yosupo.jp/problem/staticrmq", report)


if __name__ == "__main__":
    unittest.main()
