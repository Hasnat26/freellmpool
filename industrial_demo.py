"""Backward-compatible entry point for the industrial RFQ demo.

The implementation now lives in :mod:`freellmpool.industrial` so the workflow
is part of the installable package as well as the repository demo.
"""

from __future__ import annotations

import argparse
import json

from freellmpool.industrial import build_report, render_report, write_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the industrial RFQ compliance demo.")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--output", help="write the JSON report to this file")
    args = parser.parse_args()

    report = build_report()
    if args.output:
        write_report(report, args.output)
        print(f"Wrote report: {args.output}")
        return
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return
    print(render_report(report))


if __name__ == "__main__":
    main()
