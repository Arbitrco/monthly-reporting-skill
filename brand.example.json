"""
chart_helper.py — Shared SVG and brand primitives for section renderers.

This module is a starter — copy it to your working directory and reference
it from your section renderers. Update the BRAND constants from your brand
source (see references/brand-config.md in the parent meta-skill).

Two reasons to use this module:
  1. Sections that share chart geometry (line chart, bar chart) shouldn't
     reinvent it. Use these functions to get consistent visuals.
  2. Brand colours change. Updating them in one module beats updating ten
     section files.

This is SVG-only. The sections in this skill use inline SVG so the entire
report HTML is self-contained — no PNG images, no Chart.js, no external
dependencies. Inline SVG is also what WeasyPrint renders most reliably.

If you need matplotlib charts (e.g. for ad-hoc analysis outside the report),
write a separate module.
"""

import html
import math


# ---------------------------------------------------------------------------
# Brand constants — sync from your brand source
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

# Ordered palette for multi-series charts. First entry is the headline series.
BRAND_PALETTE = [BLUE, TEAL, SKY, NAVY, WARNING, ALERT]


# ---------------------------------------------------------------------------
# Standard plot area
# ---------------------------------------------------------------------------

# Most sections use viewBox 0 0 820 220 with these inner bounds.
PLOT_X_LEFT  = 44.0
PLOT_X_RIGHT = 800.0
PLOT_Y_TOP   = 16.0
PLOT_Y_BOT   = 170.0
PLOT_HEIGHT  = PLOT_Y_BOT - PLOT_Y_TOP  # 154


def x_for_index(i, n, x_left=PLOT_X_LEFT, x_right=PLOT_X_RIGHT):
    """Evenly distribute n points across [x_left, x_right]."""
    if n <= 1:
        return x_left
    return x_left + i * ((x_right - x_left) / (n - 1))


def y_for_value(v, y_max, y_top=PLOT_Y_TOP, y_bot=PLOT_Y_BOT):
    """Map a value in [0, y_max] to a y-coord in [y_top, y_bot] (inverted)."""
    if y_max <= 0:
        return y_bot
    return y_bot - (float(v) / y_max) * (y_bot - y_top)


def compute_y_max(values, round_to=5, floor=5):
    """Round the max value up to a multiple of round_to (with a sane floor)."""
    cand = [float(v) for v in values if v is not None]
    if not cand:
        return float(floor)
    raw = max(cand)
    return float(max(floor, math.ceil(raw / round_to) * round_to))


# ---------------------------------------------------------------------------
# SVG primitives
# ---------------------------------------------------------------------------

def svg_open(view_w=820, view_h=220, **attrs):
    """Open an <svg> tag with the standard viewBox and attributes."""
    attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    return (
        f'<svg viewBox="0 0 {view_w} {view_h}" width="100%" '
        f'preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" '
        f'style="overflow:visible" {attr_str}>'
    )


def svg_close():
    return '</svg>'


def gridlines(y_max, n_lines=6, x_left=PLOT_X_LEFT, x_right=PLOT_X_RIGHT,
              y_top=PLOT_Y_TOP, y_bot=PLOT_Y_BOT,
              colour=BORDER, label_colour=TEXT_MUTED,
              unit_suffix=""):
    """Horizontal gridlines + y-axis labels. Returns SVG fragment string."""
    parts = []
    step = y_max / n_lines
    for i in range(n_lines + 1):
        v = step * i
        y = y_for_value(v, y_max, y_top, y_bot)
        parts.append(
            f'<line x1="{x_left}" x2="{x_right}" '
            f'y1="{y:.2f}" y2="{y:.2f}" '
            f'stroke="{colour}" stroke-width="0.5"/>'
        )
        label = f"{int(round(v))}{unit_suffix}"
        parts.append(
            f'<text x="{x_left - 4}" y="{y + 3:.1f}" '
            f'text-anchor="end" font-size="10" fill="{label_colour}">{label}</text>'
        )
    # Axis borders
    parts.append(
        f'<line x1="{x_left}" y1="{y_top}" x2="{x_left}" y2="{y_bot}" '
        f'stroke="{colour}" stroke-width="1"/>'
    )
    parts.append(
        f'<line x1="{x_left}" y1="{y_bot}" x2="{x_right}" y2="{y_bot}" '
        f'stroke="{colour}" stroke-width="1"/>'
    )
    return "\n".join(parts)


def x_axis_labels(labels, x_left=PLOT_X_LEFT, x_right=PLOT_X_RIGHT,
                  y=200, colour=TEXT_MUTED, font_size=10):
    """X-axis category labels (one per data point)."""
    n = len(labels)
    parts = []
    for i, lbl in enumerate(labels):
        x = x_for_index(i, n, x_left, x_right)
        parts.append(
            f'<text x="{x:.1f}" y="{y}" text-anchor="middle" '
            f'font-size="{font_size}" fill="{colour}">'
            f'{html.escape(str(lbl))}</text>'
        )
    return "\n".join(parts)


def line_series(values, y_max, colour, x_left=PLOT_X_LEFT, x_right=PLOT_X_RIGHT,
                y_top=PLOT_Y_TOP, y_bot=PLOT_Y_BOT,
                stroke_width=2.5, dasharray=None, with_dots=True, dot_r=3):
    """A polyline + optional circle markers for one data series.

    None values create gaps (separate polyline segments)."""
    parts = []
    n = len(values)
    # Split into contiguous non-None runs
    runs = []
    current = []
    for i, v in enumerate(values):
        if v is None:
            if current:
                runs.append(current)
                current = []
        else:
            current.append((i, v))
    if current:
        runs.append(current)

    dash_attr = f' stroke-dasharray="{dasharray}"' if dasharray else ""

    for run in runs:
        pts = " ".join(
            f"{x_for_index(i, n, x_left, x_right):.1f},"
            f"{y_for_value(v, y_max, y_top, y_bot):.2f}"
            for i, v in run
        )
        parts.append(
            f'<polyline points="{pts}" fill="none" stroke="{colour}" '
            f'stroke-width="{stroke_width}"{dash_attr}/>'
        )
        if with_dots:
            for i, v in run:
                x = x_for_index(i, n, x_left, x_right)
                y = y_for_value(v, y_max, y_top, y_bot)
                parts.append(
                    f'<circle cx="{x:.1f}" cy="{y:.2f}" r="{dot_r}" fill="{colour}"/>'
                )
    return "\n".join(parts)


def bar_series(values, y_max, colours, x_left=PLOT_X_LEFT, x_right=PLOT_X_RIGHT,
               y_top=PLOT_Y_TOP, y_bot=PLOT_Y_BOT,
               bar_width=36):
    """Single-series bar chart. colours is a list of per-bar hex strings
    (use the same colour for all bars for a flat series; vary per bar for
    pattern-coloured bars)."""
    n = len(values)
    if isinstance(colours, str):
        colours = [colours] * n
    parts = []
    for i, v in enumerate(values):
        if v is None:
            continue
        cx = x_for_index(i, n, x_left, x_right)
        y_top_bar = y_for_value(v, y_max, y_top, y_bot)
        height = y_bot - y_top_bar
        x_bar = cx - bar_width / 2
        parts.append(
            f'<rect x="{x_bar:.1f}" y="{y_top_bar:.2f}" '
            f'width="{bar_width}" height="{height:.2f}" '
            f'fill="{colours[i]}" rx="2"/>'
        )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Legend helpers
# ---------------------------------------------------------------------------

def legend_swatch(colour, label, dashed=False, width="22px"):
    """One legend item: a small line swatch + label."""
    line = (
        f'<svg width="24" height="12">'
        f'<line x1="0" y1="6" x2="24" y2="6" stroke="{colour}" '
        f'stroke-width="2.5"'
        + (' stroke-dasharray="6 4"' if dashed else "")
        + '/></svg>'
    )
    return (
        f'<span class="ci" style="display:flex;align-items:center;gap:6px;'
        f'font-size:7.5pt;font-weight:600;color:{TEXT}">{line} {html.escape(label)}</span>'
    )


def legend_row(*items):
    """Wrap a series of legend_swatch outputs in a flex row."""
    return (
        '<div class="clg" style="display:flex;gap:20px;margin-bottom:12px">'
        + "".join(items)
        + "</div>"
    )


# ---------------------------------------------------------------------------
# Formatting helpers (currency, percent, days)
# ---------------------------------------------------------------------------

def fmt_money(v, sign=False, dp=0):
    """Format $-amounts: $X, $X.Xk, $X.XM."""
    if v is None:
        return "&mdash;"
    a = abs(float(v))
    if a >= 1e6:
        s = f"${a/1e6:.1f}M"
    elif a >= 1e4:
        s = f"${a/1e3:.0f}k"
    elif a >= 1e3:
        s = f"${a/1e3:.1f}k"
    else:
        s = f"${a:.{dp}f}"
    if sign:
        if v > 0: return "+" + s
        if v < 0: return "-" + s
        return s
    return ("-" if float(v) < 0 else "") + s


def fmt_pct(v, dp=1, sign=False):
    if v is None:
        return "&mdash;"
    body = f"{abs(float(v)):.{dp}f}%"
    if sign:
        if v > 0: return "+" + body
        if v < 0: return "-" + body
    return ("-" if float(v) < 0 else "") + body


def fmt_int(v):
    if v is None:
        return "&mdash;"
    return f"{int(v):,}"


def fmt_days(v, dp=1):
    if v is None:
        return "&mdash;"
    return f"{float(v):.{dp}f}d"


# ---------------------------------------------------------------------------
# Colour-by-threshold helpers
# ---------------------------------------------------------------------------

def colour_for_rate(pct, thresholds=None):
    """Map a percentage to a brand colour by threshold.

    Default thresholds (good / caution / alert):
        pct < 10  -> BLUE   (good)
        pct < 30  -> WARNING (caution)
        pct >= 30 -> ALERT   (bad)
    """
    if thresholds is None:
        thresholds = [(10, BLUE), (30, WARNING), (float("inf"), ALERT)]
    for cap, colour in thresholds:
        if pct < cap:
            return colour
    return thresholds[-1][1]


def colour_for_variance(v, fav_above_zero=True, threshold=50):
    """Adverse/favourable colour for a signed variance.

    fav_above_zero: True if positive = favourable (e.g. revenue above budget);
                    False if positive = adverse (e.g. costs above budget).
    """
    if abs(v) < threshold:
        return TEXT
    is_positive = v > 0
    is_favourable = is_positive == fav_above_zero
    return BLUE if is_favourable else ALERT
