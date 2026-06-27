#!/usr/bin/env python3
"""Update README.md stats section from collected job CSV data."""

import csv
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data" / "raw"
README = REPO_ROOT / "README.md"

SERIES = {
    "0854": "Computer Engineering (0854)",
    "1550": "Computer Science (1550)",
    "1560": "Data Science (1560)",
    "2210": "IT Management (2210)",
}

MARKER_START = "<!-- STATS_START -->"
MARKER_END = "<!-- STATS_END -->"

TOP_AGENCIES = 10


def load_file(path: Path) -> list[dict]:
    try:
        with path.open(newline="", encoding="utf-8") as f:
            return [r for r in csv.DictReader(f) if r.get("Job URL", "").strip()]
    except Exception as e:
        print(f"Warning: could not read {path}: {e}", file=sys.stderr)
        return []


def load_unique(pattern: str) -> list[dict]:
    """Load all CSVs matching pattern, deduplicating by Job URL."""
    seen: dict[str, dict] = {}
    for path in DATA_DIR.glob(pattern):
        for row in load_file(path):
            url = row["Job URL"].strip()
            seen[url] = row
    return list(seen.values())


def count_file_unique(path: Path) -> int:
    """Count unique Job URLs in a single file."""
    return len({r["Job URL"].strip() for r in load_file(path)})


def md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    """Render a pretty-printed (aligned) markdown table."""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    def fmt_row(cells: list[str]) -> str:
        return (
            "| "
            + " | ".join(c.ljust(col_widths[i]) for i, c in enumerate(cells))
            + " |"
        )

    sep = "| " + " | ".join("-" * w for w in col_widths) + " |"
    return [fmt_row(headers), sep] + [fmt_row(row) for row in rows]


def build_stats_section(all_jobs: list[dict], active_jobs: list[dict]) -> str:
    today = date.today().isoformat()

    series_counts = {
        code: count_file_unique(DATA_DIR / f"active_{code}_jobs.csv") for code in SERIES
    }

    agency_counter: dict[str, int] = {}
    for r in active_jobs:
        agency = r.get("Agency", "").strip()
        if agency:
            agency_counter[agency] = agency_counter.get(agency, 0) + 1
    top_agencies = sorted(agency_counter.items(), key=lambda x: -x[1])[:TOP_AGENCIES]

    lines: list[str] = [
        MARKER_START,
        "",
        "## Data Stats",
        "",
        f"> Last updated: **{today}**",
        "",
    ]

    lines += md_table(
        ["Metric", "Count"],
        [
            ["Total unique job postings tracked", f"**{len(all_jobs):,}**"],
            ["Currently active positions", f"**{len(active_jobs):,}**"],
        ],
    )

    lines += ["", "### Active Positions by Job Series", ""]
    lines += md_table(
        ["Series", "Name", "Active Postings"],
        [[code, SERIES[code], f"{series_counts[code]:,}"] for code in sorted(SERIES)],
    )

    lines += ["", "### Top Agencies (Active Postings)", ""]
    lines += md_table(
        ["Agency", "Active Postings"],
        [[agency, f"{count:,}"] for agency, count in top_agencies],
    )

    lines += ["", MARKER_END]
    return "\n".join(lines)


def update_readme(stats_section: str) -> None:
    content = README.read_text(encoding="utf-8")
    start = content.find(MARKER_START)
    end = content.find(MARKER_END)

    if start == -1 or end == -1:
        content = content.rstrip() + "\n\n" + stats_section + "\n"
    else:
        content = content[:start] + stats_section + content[end + len(MARKER_END) :]

    README.write_text(content, encoding="utf-8")


def main() -> None:
    all_jobs = load_unique("all_*_jobs.csv")
    active_jobs = load_unique("active_*_jobs.csv")

    print(f"Loaded {len(all_jobs)} total unique jobs, {len(active_jobs)} active")

    stats = build_stats_section(all_jobs, active_jobs)
    update_readme(stats)
    print("README.md updated.")


if __name__ == "__main__":
    main()
