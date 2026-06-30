#!/usr/bin/env python3
"""Render a single HTML file to PDF using WeasyPrint.

Used during workflow A for section-level QA — render one section's
fragment in isolation to check layout before integrating into the
full report.

Usage:
    python render_pdf.py --in section.html --out section.pdf
"""

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="input", required=True, help="HTML file to render")
    parser.add_argument("--out", required=True, help="Output PDF path")
    parser.add_argument(
        "--base-url",
        default=None,
        help="Base URL for resolving relative paths (default: directory of --in)",
    )
    args = parser.parse_args()

    try:
        import weasyprint  # type: ignore
    except ImportError:
        print(
            "error: weasyprint not installed. Run:\n"
            "  pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 2

    in_path = Path(args.input).resolve()
    if not in_path.exists():
        print(f"error: {in_path} not found", file=sys.stderr)
        return 1

    base_url = args.base_url or str(in_path.parent)
    weasyprint.HTML(filename=str(in_path), base_url=base_url).write_pdf(args.out)
    print(f"rendered: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
