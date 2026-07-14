#!/usr/bin/env python3
"""Compare PR-branch vs base-branch benchmark results and render a Markdown
report suitable for posting as a PR comment.

Usage:
    python benchmarks/compare.py \\
        --base-time base-time.json --pr-time pr-time.json \\
        --base-memory base-memory.json --pr-memory pr-memory.json \\
        --output report.md
"""

import argparse
import json
import re

NAME_RE = re.compile(r"\[(.+)\]$")


def _benchmark_name(raw_name):
    m = NAME_RE.search(raw_name)
    if m:
        return m.group(1)
    if raw_name.startswith("test_"):
        return raw_name[len("test_"):]
    return raw_name


def load_time_results(path):
    with open(path) as f:
        data = json.load(f)
    return {
        _benchmark_name(b["name"]): b["stats"]["mean"]
        for b in data.get("benchmarks", [])
    }


def load_memory_results(path):
    with open(path) as f:
        data = json.load(f)
    return {b["name"]: b["peak_bytes"] for b in data.get("benchmarks", [])}


def fmt_time(seconds):
    if seconds < 1e-3:
        return f"{seconds * 1e6:.1f}µs"
    if seconds < 1:
        return f"{seconds * 1e3:.2f}ms"
    return f"{seconds:.3f}s"


def fmt_bytes(n):
    value = float(n)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if abs(value) < 1024:
            return f"{value:.1f}{unit}"
        value /= 1024
    return f"{value:.1f}TiB"


def fmt_delta(base, pr):
    if base == 0:
        return "n/a"
    pct = (pr - base) / base * 100
    if pct <= -1:
        mark = "✅"
    elif pct > 5:
        mark = "⚠️"
    else:
        mark = ""
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}% {mark}".strip()


def build_table(names, base_map, pr_map, fmt_value):
    lines = ["| Benchmark | Base | PR | Delta |", "|---|---|---|---|"]
    for name in names:
        base_v = base_map.get(name)
        pr_v = pr_map.get(name)
        if base_v is None or pr_v is None:
            lines.append(f"| {name} | {'n/a' if base_v is None else fmt_value(base_v)} | "
                         f"{'n/a' if pr_v is None else fmt_value(pr_v)} | n/a |")
            continue
        lines.append(f"| {name} | {fmt_value(base_v)} | {fmt_value(pr_v)} | {fmt_delta(base_v, pr_v)} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-time", required=True)
    parser.add_argument("--pr-time", required=True)
    parser.add_argument("--base-memory", required=True)
    parser.add_argument("--pr-memory", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    base_time = load_time_results(args.base_time)
    pr_time = load_time_results(args.pr_time)
    base_memory = load_memory_results(args.base_memory)
    pr_memory = load_memory_results(args.pr_memory)

    time_names = sorted(set(base_time) | set(pr_time))
    memory_names = sorted(set(base_memory) | set(pr_memory))

    report = ["## \U0001F4CA Performance Benchmark Results", ""]
    if not time_names and not memory_names:
        report.append("No benchmark results were produced.")
    else:
        report.append("### ⏱️ Execution time (mean, lower is better)")
        report.append(build_table(time_names, base_time, pr_time, fmt_time) if time_names else "n/a")
        report.append("")
        report.append("### \U0001F4BE Peak memory (lower is better)")
        report.append(build_table(memory_names, base_memory, pr_memory, fmt_bytes) if memory_names else "n/a")
        report.append("")
        report.append(
            "<sub>Base = target branch, PR = this branch. Negative delta = improvement. "
            "✅ improvement ≥ 1%, ⚠️ regression > 5%. "
            "\"n/a\" base entries mean the target branch has no benchmark suite yet.</sub>"
        )

    text = "\n".join(report)
    with open(args.output, "w") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
