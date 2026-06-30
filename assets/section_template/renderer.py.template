#!/usr/bin/env python3
"""
sections/{{SECTION_SLUG}}/renderer.py

Generates the {{SECTION_TITLE}} HTML fragment for the monthly operational
report (Section {{SECTION_NUMBER}}).

Reads a JSON of rows from {{VIEW_NAME}}, writes a self-contained HTML
fragment to the path given by --output.

Usage:
    python renderer.py \\
        --rows           rows.json \\
        --period         "April 2026" \\
        --output         fragment.html \\
        [--auto-commentary       "<paragraph text>"] \\
        [--user-commentary       "<verbatim text>"] \\
        [--user-commentary-file  path/to/notes.txt]

Commentary handling:
  Auto-commentary is HTML-escaped and inserted as <p> paragraphs inside .cmtb.
  User commentary is HTML-escaped and inserted inside the .add-note sub-block.
  Neither is paraphrased, summarised, or otherwise transformed — see the
  parent meta-skill's commentary-verbatim.md.
"""

import argparse
import html
import json
import sys
from datetime import datetime


# ---------------------------------------------------------------------------
# Brand constants — sync from the brand source (skill or brand.json)
# ---------------------------------------------------------------------------

NAVY        = "#004673"
BLUE        = "#1C72B5"
SKY         = "#37A6DE"
TEAL        = "#27CED7"
ALERT       = "#C0392B"
WARNING     = "#E67E22"
TEXT        = "#535B62"
TEXT_MUTED  = "#727C87"
TEXT_SUBTLE = "#9AA2AD"
BORDER      = "#DFE3E5"
BG_PAGE     = "#F4F6F8"
BG_CARD     = "#FFFFFF"
FONT        = "'Ruda',Calibri,sans-serif"

SECTION_N     = {{SECTION_NUMBER}}
SECTION_TITLE = "{{SECTION_TITLE}}"
VIEW_NAME     = "{{VIEW_NAME}}"


# ---------------------------------------------------------------------------
# Scoped CSS
# ---------------------------------------------------------------------------

def scoped_css():
    n = SECTION_N
    return f"""\
@import url('https://fonts.googleapis.com/css2?family=Ruda:wght@400;500;600;700;800;900&display=swap');
#section-{n}{{font-family:{FONT};background:{BG_PAGE};width:8.5in;box-sizing:border-box;page-break-before:always}}
#section-{n} .shb{{background:{NAVY};padding:0 48px;height:56px;display:flex;justify-content:space-between;align-items:center}}
#section-{n} .shb h2{{font-size:13pt;font-weight:800;color:#fff;margin:0;letter-spacing:1px;text-transform:uppercase}}
#section-{n} .shl{{background:#fff;border-radius:4px;padding:4px 8px;height:36px;display:flex;align-items:center}}
#section-{n} .shl img{{height:26px}}
#section-{n} .sc{{padding:28px 48px 36px}}
#section-{n} .sn{{font-size:7.5pt;color:{TEXT_MUTED};margin-bottom:20px;padding:8px 12px;background:#fff;border-radius:6px;border-left:3px solid {BORDER}}}
#section-{n} .ks{{display:flex;gap:12px;margin-bottom:20px}}
#section-{n} .kc{{flex:1;background:#fff;border-radius:8px;border-top:3px solid {SKY};padding:14px 16px;box-shadow:0 2px 8px rgba(0,0,0,.07)}}
#section-{n} .kl{{font-size:7pt;font-weight:800;color:{NAVY};text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px}}
#section-{n} .kv{{font-size:22pt;font-weight:800;color:{SKY};line-height:1}}
#section-{n} .ks2{{font-size:7pt;color:{TEXT_MUTED};margin-top:4px}}
#section-{n} .chart-wrap{{background:#fff;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.07);padding:16px;margin-bottom:20px;page-break-inside:avoid;break-inside:avoid}}
#section-{n} .cht{{font-size:8pt;font-weight:800;color:{NAVY};text-transform:uppercase;letter-spacing:.5px;margin-bottom:10px}}
#section-{n} .cmtb{{background:#fff;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.07);padding:16px 18px;margin-bottom:20px}}
#section-{n} .cmtb p{{font-size:8.5pt;color:#3D4550;line-height:1.6;margin:0 0 10px}}
#section-{n} .cmtb p:last-child{{margin-bottom:0}}
#section-{n} .cmtb .add-note{{border-left:3px solid {SKY};padding:10px 14px;font-style:italic;background:{BG_PAGE};border-radius:0 6px 6px 0;margin-top:10px}}
#section-{n} .cmtb .add-note p{{margin:0 0 8px;white-space:pre-wrap}}
#section-{n} .cmtb .add-note p:last-child{{margin-bottom:0}}
#section-{n} .cmtb .add-note .lbl{{color:{NAVY};font-style:normal;text-transform:uppercase;letter-spacing:.5px;font-size:8pt;font-weight:800;display:block;margin-bottom:4px}}
#section-{n} .src{{font-size:7pt;color:{TEXT_SUBTLE};margin-top:14px}}"""


# ---------------------------------------------------------------------------
# Commentary renderer — the verbatim rule, encoded in code
# ---------------------------------------------------------------------------

def render_commentary(auto, user_verbatim):
    """
    Render the commentary block.

    auto: Claude's data-driven draft. HTML-escaped, paragraphs split on
          double newline.
    user_verbatim: user's text. HTML-escaped only — never paraphrased,
          summarised, typo-corrected, or punctuation-substituted.
    """
    if not auto and not user_verbatim:
        return ""

    parts = ['  <div class="cmtb">']

    if auto:
        for p in [x.strip() for x in auto.strip().split("\n\n") if x.strip()]:
            parts.append(f'    <p>{html.escape(p, quote=False)}</p>')

    if user_verbatim:
        parts.append('    <div class="add-note">')
        parts.append('      <span class="lbl">Additional notes</span>')
        for vp in [x for x in user_verbatim.strip().split("\n\n") if x.strip()]:
            parts.append(f'      <p>{html.escape(vp, quote=False)}</p>')
        parts.append('    </div>')

    parts.append('  </div>')
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_money(v):
    """Format a number as $X, $X.Xk, or $X.XM depending on magnitude."""
    if v is None:
        return "&mdash;"
    a = abs(float(v))
    if a >= 1e6:
        s = f"${a/1e6:.1f}M"
    elif a >= 1e3:
        s = f"${a/1e3:.0f}k"
    else:
        s = f"${a:.0f}"
    return ("-" if float(v) < 0 else "") + s


def fmt_pct(v, dp=1):
    if v is None:
        return "&mdash;"
    return f"{float(v):.{dp}f}%"


def fmt_int(v):
    if v is None:
        return "&mdash;"
    return f"{int(v):,}"


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------

def kpi_card(label, value, sub, top_colour=None, value_colour=None):
    """One KPI card. Use top_colour=ALERT to highlight as adverse."""
    top = top_colour or SKY
    val_col = value_colour or SKY
    return (
        f'<div class="kc" style="border-top-color:{top}">'
        f'  <div class="kl">{label}</div>'
        f'  <div class="kv" style="color:{val_col}">{value}</div>'
        f'  <div class="ks2">{sub}</div>'
        f'</div>'
    )


def kpi_row(*cards):
    return f'<div class="ks">{"".join(cards)}</div>'


# ---------------------------------------------------------------------------
# Optional: inline SVG chart helpers
# Copy from /assets/chart_helper.py or import from a sibling module if you
# share helpers across sections.
# ---------------------------------------------------------------------------

# PLOT_X_LEFT  = 44.0
# PLOT_X_RIGHT = 800.0
# PLOT_Y_TOP   = 16.0
# PLOT_Y_BOT   = 170.0
#
# def x_for_index(i, n):
#     if n <= 1:
#         return PLOT_X_LEFT
#     return PLOT_X_LEFT + i * ((PLOT_X_RIGHT - PLOT_X_LEFT) / (n - 1))
#
# def y_for_value(v, y_max):
#     return PLOT_Y_BOT - (float(v) / y_max) * (PLOT_Y_BOT - PLOT_Y_TOP)


# ---------------------------------------------------------------------------
# Fragment builder
# ---------------------------------------------------------------------------

def build_fragment(payload, period, auto_commentary, user_commentary):
    """
    Build the full HTML fragment.

    REPLACE this function body with the section-specific layout. The
    skeleton below shows the standard structure.
    """
    # ----- REPLACE: extract data from payload -----
    rows = payload.get("rows", [])  # adjust to match the actual JSON schema
    if not rows:
        raise SystemExit("ERROR: payload contains no rows")

    # ----- REPLACE: compute KPI values from rows -----
    # Example: total = sum(r["amount"] for r in rows)
    # Example: count = len(rows)

    # ----- KPI cards (REPLACE labels and values) -----
    kpis = kpi_row(
        kpi_card("LABEL 1", "VALUE 1", "Sub 1"),
        kpi_card("LABEL 2", "VALUE 2", "Sub 2"),
        kpi_card("LABEL 3", "VALUE 3", "Sub 3"),
    )

    # ----- Commentary -----
    commentary_html = render_commentary(auto_commentary, user_commentary)

    # ----- Source note -----
    today = datetime.today().strftime("%d %B %Y").lstrip("0")
    source_note = (
        f'  <p class="src">Source: {VIEW_NAME} &middot; '
        f'Generated {today}.</p>'
    )

    # ----- Assemble -----
    return f"""<div class="report-section" id="section-{SECTION_N}">
<style>
{scoped_css()}
</style>

  <div class="shb">
    <h2>{SECTION_N}. {html.escape(SECTION_TITLE)}</h2>
  </div>

  <div class="sc">
    <p class="sn">[REPLACE: one-paragraph scope note describing what
this section measures and what data source it uses.]</p>

    {kpis}

    {commentary_html}

{source_note}
  </div>
</div>
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def read_text_arg(direct, file_path):
    if direct:
        return direct
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--rows",   required=True, help="Path to rows JSON")
    p.add_argument("--period", required=True, help='Display label e.g. "April 2026"')
    p.add_argument("--output", required=True, help="Output fragment path")
    p.add_argument("--auto-commentary", default="", dest="auto_commentary")
    p.add_argument("--user-commentary", default="", dest="user_commentary")
    p.add_argument("--user-commentary-file", default=None, dest="user_commentary_file")
    args = p.parse_args()

    try:
        with open(args.rows, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR reading {args.rows}: {e}", file=sys.stderr)
        sys.exit(1)

    user_text = read_text_arg(args.user_commentary, args.user_commentary_file)
    html_out = build_fragment(payload, args.period, args.auto_commentary, user_text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html_out)

    print(f"Section {SECTION_N} fragment written: {args.output} ({len(html_out):,} chars)")


if __name__ == "__main__":
    main()
