#!/usr/bin/env python3
"""Scaffold a new section sub-skill (workflow doc + Python renderer).

Usage:
    python new_section.py --name credit-note-analysis \\
                          --title "Credit Note Analysis" \\
                          --number 5 \\
                          --view vw_InvoiceCreditNoteStatus \\
                          --out sections/

Creates:
    sections/<name>/SKILL.md      (from assets/section_template/SKILL.md)
    sections/<name>/renderer.py   (from assets/section_template/renderer.py)

The user then fills in the queries, KPI definitions, HTML layout, and
commentary guidance.
"""

import argparse
import re
import sys
from pathlib import Path


def substitute(text, name, title, number, view):
    """Apply all template substitutions."""
    return (
        text.replace("{{SECTION_SLUG}}", name)
            .replace("{{SECTION_TITLE}}", title)
            .replace("{{SECTION_NUMBER}}", str(number))
            .replace("{{VIEW_NAME}}", view)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--name",   required=True, help="Section slug (kebab-case)")
    parser.add_argument("--title",  required=True, help="Display title")
    parser.add_argument("--number", required=True, type=int,
                        help="Section number (used in #section-N and fragment filename)")
    parser.add_argument("--view",   required=True, help="dataSights view name (vw_*)")
    parser.add_argument("--out",    default="sections", help="Sections directory")
    parser.add_argument(
        "--template-dir",
        default=None,
        help="Path to template directory "
             "(default: ../assets/section_template relative to this script)",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing section")
    args = parser.parse_args()

    # Validate slug
    if not re.fullmatch(r"[a-z][a-z0-9-]*", args.name):
        print(f"error: --name must be kebab-case (got {args.name!r})", file=sys.stderr)
        return 2

    # Validate view name
    if not args.view.startswith("vw_"):
        print(f"error: --view should start with 'vw_' (got {args.view!r})",
              file=sys.stderr)
        return 2

    # Validate section number
    if args.number < 1 or args.number > 99:
        print(f"error: --number must be between 1 and 99 (got {args.number})",
              file=sys.stderr)
        return 2

    script_dir = Path(__file__).resolve().parent
    template_dir = (
        Path(args.template_dir)
        if args.template_dir
        else script_dir.parent / "assets" / "section_template"
    )
    template_skill = template_dir / "SKILL.md.template"
    template_renderer = template_dir / "renderer.py.template"

    if not template_skill.exists():
        print(f"error: SKILL.md.template not found at {template_skill}", file=sys.stderr)
        return 2
    if not template_renderer.exists():
        print(f"error: renderer.py.template not found at {template_renderer}", file=sys.stderr)
        return 2

    section_dir = Path(args.out) / args.name
    skill_md_out = section_dir / "SKILL.md"
    renderer_out = section_dir / "renderer.py"

    if (skill_md_out.exists() or renderer_out.exists()) and not args.force:
        print(f"error: {section_dir} already contains files. Use --force to overwrite.",
              file=sys.stderr)
        return 1

    section_dir.mkdir(parents=True, exist_ok=True)

    # Write SKILL.md
    skill_text = template_skill.read_text(encoding="utf-8")
    skill_md_out.write_text(
        substitute(skill_text, args.name, args.title, args.number, args.view),
        encoding="utf-8",
    )
    print(f"created: {skill_md_out}")

    # Write renderer.py
    renderer_text = template_renderer.read_text(encoding="utf-8")
    renderer_out.write_text(
        substitute(renderer_text, args.name, args.title, args.number, args.view),
        encoding="utf-8",
    )
    # Mark renderer as executable on POSIX systems
    try:
        renderer_out.chmod(0o755)
    except (OSError, NotImplementedError):
        pass
    print(f"created: {renderer_out}")

    print()
    print(f"Section {args.number} — {args.title} scaffolded at {section_dir}/")
    print()
    print("Next steps:")
    print(f"  1. Fill in the queries section in {skill_md_out}")
    print(f"     against {args.view}")
    print(f"  2. Fill in build_fragment() in {renderer_out}")
    print("     (KPI cards, chart, scope note, source note)")
    print("  3. Fill in commentary guidance and interpretive notes in SKILL.md")
    print(f"  4. Test by running:")
    print(f"       python {renderer_out} \\")
    print(f"         --rows   reports/fragments/<period>-section-{args.number}-rows.json \\")
    print(f"         --period \"<period>\" \\")
    print(f"         --output reports/fragments/<period>-section-{args.number}.html")
    print("  5. Add the section to report_order.json (if used)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
