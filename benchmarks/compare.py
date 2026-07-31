#!/usr/bin/env python3
"""Compare PR-branch vs base-branch benchmark results and render a Markdown
report suitable for posting as a PR comment.

Usage:
    python benchmarks/compare.py \\
        --base-time base-time-*.json --pr-time pr-time-*.json \\
        --base-memory base-memory.json --pr-memory pr-memory.json \\
        --output report.md

Several time files may be given per side: the workflow runs the two branches in
interleaved passes so that drift on the runner hits both sides equally.  For
each workload we keep the *minimum* observed time across all rounds of all
passes.  The minimum is the right statistic here -- interference from
neighbouring jobs can only ever make a run slower, so the fastest observation
is the closest estimate of the code's actual cost, while the mean mostly
measures how busy the runner was.

A delta is only called a win or a regression when it is larger than the noise
we actually observed between passes (and never below ``MIN_SIGNIFICANT``).
Reporting "1% faster" from a single noisy pair of runs is how a benchmark ends
up disagreeing with the judge.
"""

import argparse
import json
import re

NAME_RE = re.compile(r"\[(.+)\]$")

# A delta smaller than this is never reported as a change, however quiet the
# runner looked. GitHub-hosted runners do not do better than a few percent.
MIN_SIGNIFICANT = 0.03

# tracemalloc peaks are deterministic, so memory needs only a token allowance.
MEMORY_SIGNIFICANT = 0.01

LIBRARY_CHECKER = "https://judge.yosupo.jp/problem/"


def _benchmark_name(raw_name):
    m = NAME_RE.search(raw_name)
    if m:
        return m.group(1)
    if raw_name.startswith("test_"):
        return raw_name[len("test_") :]
    return raw_name


def load_time_results(paths):
    """Return {name: {"samples": [per-pass minimum, ...], "info": {...}}}."""
    results = {}
    for path in paths:
        try:
            with open(path) as f:
                data = json.load(f)
        except (OSError, ValueError):
            continue
        for b in data.get("benchmarks", []):
            name = _benchmark_name(b["name"])
            entry = results.setdefault(name, {"samples": [], "info": {}})
            # "min" is best-of-rounds within this pass.
            entry["samples"].append(b["stats"]["min"])
            entry["info"].update(b.get("extra_info") or {})
    return results


def load_memory_results(paths):
    results = {}
    for path in paths:
        try:
            with open(path) as f:
                data = json.load(f)
        except (OSError, ValueError):
            continue
        for b in data.get("benchmarks", []):
            results[b["name"]] = b["peak_bytes"]
    return results


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


def spread(samples):
    """Relative gap between the slowest and fastest pass: our noise estimate."""
    if len(samples) < 2:
        return 0.0
    best = min(samples)
    if best <= 0:
        return 0.0
    return (max(samples) - best) / best


def fmt_delta(base, pr, threshold):
    if base == 0:
        return "n/a"
    if base == pr:
        return "0.0%"
    pct = (pr - base) / base * 100
    sign = "+" if pct >= 0 else ""
    if abs(pct) < threshold * 100:
        return f"{sign}{pct:.1f}% ≈"
    mark = "✅" if pct < 0 else "⚠️"
    return f"{sign}{pct:.1f}% {mark}"


def fmt_pct(fraction):
    """Percentage that stays informative below 1% (sizes can be tiny in CI)."""
    pct = fraction * 100
    if pct >= 10:
        return f"{pct:.0f}%"
    if pct >= 1:
        return f"{pct:.1f}%"
    return f"{pct:.2f}%"


def name_cell(name, info):
    problem = (info or {}).get("problem")
    if problem:
        return f"[{name}]({LIBRARY_CHECKER}{problem})"
    return name


def build_time_table(names, base, pr, base_label="Base", pr_label="PR"):
    lines = [
        f"| Benchmark | {base_label} | {pr_label} | Delta | Noise |",
        "|---|---|---|---|---|",
    ]
    for name in names:
        base_entry = base.get(name)
        pr_entry = pr.get(name)
        info = (pr_entry or base_entry or {}).get("info", {})
        label = name_cell(name, info)
        if not base_entry or not pr_entry:
            base_cell = fmt_time(min(base_entry["samples"])) if base_entry else "n/a"
            pr_cell = fmt_time(min(pr_entry["samples"])) if pr_entry else "n/a"
            lines.append(f"| {label} | {base_cell} | {pr_cell} | n/a | n/a |")
            continue
        base_v = min(base_entry["samples"])
        pr_v = min(pr_entry["samples"])
        noise = max(spread(base_entry["samples"]), spread(pr_entry["samples"]))
        threshold = max(MIN_SIGNIFICANT, noise)
        lines.append(
            f"| {label} | {fmt_time(base_v)} | {fmt_time(pr_v)} | "
            f"{fmt_delta(base_v, pr_v, threshold)} | ±{noise * 100:.1f}% |"
        )
    return "\n".join(lines)


def build_memory_table(names, base, pr, base_label="Base", pr_label="PR"):
    lines = [f"| Benchmark | {base_label} | {pr_label} | Delta |", "|---|---|---|---|"]
    for name in names:
        base_v = base.get(name)
        pr_v = pr.get(name)
        if base_v is None or pr_v is None:
            lines.append(
                f"| {name} | {'n/a' if base_v is None else fmt_bytes(base_v)} | "
                f"{'n/a' if pr_v is None else fmt_bytes(pr_v)} | n/a |"
            )
            continue
        lines.append(
            f"| {name} | {fmt_bytes(base_v)} | {fmt_bytes(pr_v)} | "
            f"{fmt_delta(base_v, pr_v, MEMORY_SIGNIFICANT)} |"
        )
    return "\n".join(lines)


def split_names(names, base, pr):
    """Library-Checker-calibrated names first, uncalibrated extras second."""
    calibrated, extras = [], []
    for name in names:
        info = (pr.get(name) or base.get(name) or {}).get("info", {})
        if info.get("problem") or not name.startswith("extra_"):
            calibrated.append(name)
        else:
            extras.append(name)
    return calibrated, extras


def scale_note(base, pr):
    scales = {
        entry["info"].get("global_scale")
        for entry in list(base.values()) + list(pr.values())
        if entry.get("info", {}).get("global_scale")
    }
    if len(scales) == 1:
        return f"Workloads ran at `ACL_BENCH_SCALE={scales.pop()}`."
    if len(scales) > 1:
        return (
            "⚠️ Base and PR ran at different `ACL_BENCH_SCALE` values "
            f"({sorted(scales)}); the times are not comparable."
        )
    return ""


def build_size_table(names, base, pr):
    """What each workload actually ran, relative to the judge's constraints."""
    rows = []
    for name in names:
        info = (pr.get(name) or base.get(name) or {}).get("info", {})
        full_size = info.get("full_size")
        if not full_size:
            continue
        scale = info.get("scale")
        pct = fmt_pct(scale) if isinstance(scale, (int, float)) else "?"
        note = info.get("note") or ""
        rows.append(f"| {name_cell(name, info)} | {full_size} | {pct} | {note} |")
    if not rows:
        return ""
    return "\n".join(
        ["| Benchmark | Library Checker max | Ran at | Note |", "|---|---|---|---|"]
        + rows
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-time", required=True, nargs="+")
    parser.add_argument("--pr-time", required=True, nargs="+")
    parser.add_argument("--base-memory", required=True, nargs="+")
    parser.add_argument("--pr-memory", required=True, nargs="+")
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--only",
        default="",
        help=(
            "comma-separated workload names to report. Pull requests benchmark "
            "only the modules they touch, so without this the table would pad "
            "itself with n/a rows for workloads that were deliberately skipped."
        ),
    )
    parser.add_argument("--base-label", default="Base")
    parser.add_argument("--pr-label", default="PR")
    parser.add_argument("--title", default="\U0001f4ca Performance Benchmark Results")
    args = parser.parse_args()

    base_time = load_time_results(args.base_time)
    pr_time = load_time_results(args.pr_time)
    base_memory = load_memory_results(args.base_memory)
    pr_memory = load_memory_results(args.pr_memory)

    time_names = sorted(set(base_time) | set(pr_time))
    memory_names = sorted(set(base_memory) | set(pr_memory))
    if args.only:
        wanted = {n.strip() for n in args.only.split(",") if n.strip()}
        time_names = [n for n in time_names if n in wanted]
        memory_names = [n for n in memory_names if n in wanted]
    calibrated, extras = split_names(time_names, base_time, pr_time)

    report = [f"## {args.title}", ""]
    if not time_names and not memory_names:
        report.append("No benchmark results were produced.")
    else:
        note = scale_note(base_time, pr_time)
        if note:
            report.append(note)
            report.append("")
        report.append("### ⏱️ Library Checker workloads (best of N, lower is better)")
        report.append(
            build_time_table(
                calibrated, base_time, pr_time, args.base_label, args.pr_label
            )
            if calibrated
            else "n/a"
        )
        report.append("")
        if extras:
            report.append(
                "<details><summary>\U0001f9ea API coverage workloads (not judge-calibrated)</summary>"
            )
            report.append("")
            report.append(
                build_time_table(
                    extras, base_time, pr_time, args.base_label, args.pr_label
                )
            )
            report.append("")
            report.append("</details>")
            report.append("")
        size_table = build_size_table(calibrated + extras, base_time, pr_time)
        if size_table:
            report.append("<details><summary>\U0001f4cf Workload sizes</summary>")
            report.append("")
            report.append(size_table)
            report.append("")
            report.append("</details>")
            report.append("")
        report.append(
            "<details><summary>\U0001f4be Peak memory (lower is better)</summary>"
        )
        report.append("")
        report.append(
            build_memory_table(
                memory_names, base_memory, pr_memory, args.base_label, args.pr_label
            )
            if memory_names
            else "n/a"
        )
        report.append("")
        report.append("</details>")
        report.append("")
        report.append(
            "<sub>Only the workloads whose module the change touches are measured; "
            "a scheduled sweep covers the rest. Each workload mirrors the "
            "linked Library Checker problem: same query mix, same operators, same "
            "value ranges as that problem's <code>max_random</code> generator. "
            "Times are the best observation across interleaved passes; "
            "<b>Noise</b> is the spread between passes. "
            "✅ improvement / ⚠️ regression are only shown when the delta "
            "exceeds both 3% and the measured noise; ≈ means the difference is "
            "not distinguishable from noise. "
            "API-coverage workloads exist to catch regressions in methods no judge "
            "problem exercises — do not quote their timings as speedups. "
            '"n/a" rows mean one side has no such benchmark.</sub>'
        )

    text = "\n".join(report)
    with open(args.output, "w") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
