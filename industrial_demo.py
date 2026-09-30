"""Standalone demo entry point for Industrial RFQ Intelligence.\n\nThe installable product CLI is ``industrial-rfq-intelligence``. This script is\nkept as a small backward-compatible demo launcher and delegates to the\nindustrial RFQ workflow without changing the package API.\n"""

from __future__ import annotations

import argparse
import json

from freellmpool.industrial import build_report, render_report, write_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Industrial RFQ Intelligence engineering demo.")
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
