"""Tests for diff-based benchmark selection.

Selecting too little silently stops measuring a module; selecting too much
burns the Actions time this exists to save. Both directions are checked.
"""

import importlib
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "benchmarks"
    ),
)

import select_workloads as select_mod  # noqa: E402
import workloads as W  # noqa: E402


class TestSelect(unittest.TestCase):
    def test_unrelated_change_selects_nothing(self):
        self.assertEqual(select_mod.select(["README.md", "pyproject.toml"]), [])

    def test_empty_diff_selects_nothing(self):
        self.assertEqual(select_mod.select([]), [])
        self.assertEqual(select_mod.select(["", "  "]), [])

    def test_module_change_selects_only_its_workloads(self):
        names = select_mod.select(["segtree.py"])
        self.assertEqual(
            names,
            ["staticrmq", "point_set_range_composite", "extra_segtree_binary_search"],
        )

    def test_selection_covers_every_workload_of_the_module(self):
        for module in {w.module for w in W.BENCHMARKS}:
            names = set(select_mod.select([f"{module}.py"]))
            expected = {w.name for w in W.BENCHMARKS if w.module == module}
            self.assertEqual(names, expected, module)

    def test_multiple_modules_are_unioned(self):
        names = select_mod.select(["dsu.py", "scc.py"])
        self.assertEqual(names, ["unionfind", "scc", "extra_dsu_groups"])

    def test_result_is_in_registry_order(self):
        order = [w.name for w in W.BENCHMARKS]
        names = select_mod.select(["prime_fact.py", "segtree.py", "fps.py"])
        self.assertEqual(names, [n for n in order if n in set(names)])

    def test_workload_change_selects_everything(self):
        self.assertEqual(
            select_mod.select(["benchmarks/workloads.py"]),
            [w.name for w in W.BENCHMARKS],
        )

    def test_harness_change_selects_everything(self):
        for path in (
            "benchmarks/test_time.py",
            "benchmarks/memory_bench.py",
            "benchmarks/select_workloads.py",
            ".github/workflows/benchmark.yml",
        ):
            self.assertEqual(len(select_mod.select([path])), len(W.BENCHMARKS), path)

    def test_report_only_change_selects_nothing(self):
        # compare.py renders the report; it cannot change a measurement.
        self.assertEqual(select_mod.select(["benchmarks/compare.py"]), [])

    def test_leading_dot_slash_is_tolerated(self):
        self.assertEqual(select_mod.select(["./dsu.py"]), select_mod.select(["dsu.py"]))

    def test_nested_file_with_a_module_name_is_not_matched(self):
        # tests/segtree.py is not the library module.
        self.assertEqual(select_mod.select(["tests/segtree.py"]), [])

    def test_every_module_file_is_mapped(self):
        for w in W.BENCHMARKS:
            self.assertIn(f"{w.module}.py", select_mod.MODULE_FILE)


class TestOnlyFilter(unittest.TestCase):
    """``ACL_BENCH_ONLY`` is how the selection reaches both runners."""

    def reload_with(self, value):
        if value is None:
            os.environ.pop("ACL_BENCH_ONLY", None)
        else:
            os.environ["ACL_BENCH_ONLY"] = value
        importlib.reload(W)

    def tearDown(self):
        self.reload_with(None)

    def test_unset_runs_everything(self):
        self.reload_with(None)
        self.assertEqual(len(W.SELECTED), len(W.BENCHMARKS))

    def test_blank_runs_everything(self):
        self.reload_with("   ")
        self.assertEqual(len(W.SELECTED), len(W.BENCHMARKS))

    def test_filters_to_the_named_workloads(self):
        self.reload_with("scc,unionfind")
        self.assertEqual([w.name for w in W.SELECTED], ["unionfind", "scc"])

    def test_whitespace_is_tolerated(self):
        self.reload_with(" scc , unionfind ")
        self.assertEqual([w.name for w in W.SELECTED], ["unionfind", "scc"])

    def test_unknown_name_is_rejected(self):
        # A typo would silently benchmark nothing, and the report would look
        # like a clean run.
        with self.assertRaises(ValueError) as ctx:
            self.reload_with("segtree")
        self.assertIn("segtree", str(ctx.exception))

    def test_selection_output_is_accepted_by_the_filter(self):
        names = select_mod.select(["segtree.py"])
        self.reload_with(",".join(names))
        self.assertEqual([w.name for w in W.SELECTED], names)


if __name__ == "__main__":
    unittest.main()
