# Section anatomy

Every section consists of **two files** that work together:

1. `SKILL.md` — the workflow doc. Defines the data source, queries,
   commentary guidance, and QA checklist. Read by Claude every time the
   section runs.
2. `renderer.py` — a Python script with a fixed CLI. Takes a rows JSON
   plus commentary flags, writes a self-contained HTML fragment.

Both live in `sections/<section-slug>/`. The scaffolder
(`scripts/new_section.py`) produces both from templates.

## Why two files

The workflow doc is read by Claude; the renderer is run by Claude. The
split exists because:

- The SQL, period derivation, and commentary suggestions need natural
  language and contextual judgement — Claude handles those.
- The SVG geometry, scoped CSS, HTML escaping, and column formatting are
  deterministic and shouldn't depend on Claude getting them right every
  month — the renderer handles those.

Re-running the renderer with the same JSON inputs produces byte-identical
HTML. That's the point.

## The renderer's CLI contract

Every section renderer accepts the same flags:

| Flag | Required | Purpose |
|---|---|---|
| `--rows PATH` | yes | Path to the JSON of query results |
| `--period STR` | yes | Display label, e.g. `"April 2026"` |
| `--output PATH` | yes | Where to write the HTML fragment |
| `--auto-commentary STR` | no | Claude's data-driven draft (HTML-escaped, paragraphs on double newline) |
| `--user-commentary STR` | no | User's text, rendered verbatim |
| `--user-commentary-file PATH` | no | Alternative to `--user-commentary` for long input |

The two commentary flags are independent. The renderer produces:

- No commentary block at all if both are empty.
- Auto only — paragraphs inside `.cmtb`, no `.add-note`.
- User only — empty `.cmtb` with just the `.add-note` sub-block.
- Both — auto paragraphs followed by `.add-note` sub-block.

## The HTML fragment contract

Every section's renderer emits a fragment that:

- Starts with `<div class="report-section" id="section-{N}">` and ends
  with `</div>`.
- Contains no outer `<!DOCTYPE>`, `<html>`, `<head>`, or `<body>` tags.
- Includes a scoped `<style>` block with every selector prefixed
  `#section-{N}` so styles don't bleed into adjacent sections.
- Declares `page-break-before: always` on the outer `#section-{N}` so
  each section starts on a new PDF page.
- Includes the standard `.shb` navy header band with the section title
  left-aligned. The right side is left empty — the assembler injects
  the brand logo box at assembly time.
- Has no per-section footer. The assembler adds a single global footer.
- Uses **inline SVG only** for charts. No `<canvas>`, no `<script>`, no
  Chart.js — those don't render in WeasyPrint's PDF.

## Workflow doc (`SKILL.md`) structure

### Frontmatter

```yaml
---
name: <section-slug>
description: >
  Generates the <topic> section for the monthly report. Use this skill
  whenever the report needs <topic>, <synonym>, or <related-metric>.
  Triggers include "add the <topic> section", "include <topic-metric>",
  "run <topic> analysis", or any request to report on <topic-domain>.
compatibility: >
  Requires dataSights:query. HTML output produced by
  sections/<slug>/renderer.py.
---
```

The description should be pushy (sections tend to under-trigger), include
3–5 synonym phrases, and list specific quoted trigger phrases.

### Sections, in order

1. **Background & logic** — what this measures, why, any non-obvious
   business context (e.g. why EOM invoices are excluded).
2. **Reporting period** — the rule with a worked example. Common
   patterns: trailing 12 months, single month, FY-YTD, rolling 13 months.
3. **Queries** — one or more SQL queries against a single view. Each
   query has a heading explaining what it returns.
4. **JSON schema** — the structure the rows JSON should take. The
   renderer reads this directly.
5. **Render preview** — the bash invocation with no commentary flags.
6. **Auto-narrative guidance** — what the data-driven commentary should
   cover. Pattern-keyed phrasings (e.g. for a "credit rate", say what
   to lead with at 0–5%, 5–15%, >15%). Standard interpretive notes.
7. **User commentary collection** — the verbatim rule, the prompt to
   ask the user, the re-render invocation with both commentary flags.
8. **QA checklist** — items to verify before delivering.
9. **Output contract** — restating the fragment rules (page-break,
   scoped CSS, no footer, inline SVG only). Useful for future maintainers.
10. **View dependency chain** — what views/tables the section depends on.
11. **Drill-down queries** — useful ad-hoc queries against the same view
    for follow-up during commentary gathering.
12. **SVG geometry** (reference only — encoded in `renderer.py`) — for
    reviewers and anyone extending the renderer.

## Renderer (`renderer.py`) structure

The template produces a working skeleton. Sections to customise:

### 1. Brand constants (top of file)

```python
# Brand constants — synced from brand source (skill or brand.json).
NAVY     = "#004673"
BLUE     = "#1C72B5"
SKY      = "#37A6DE"
ALERT    = "#C0392B"
WARNING  = "#E67E22"
TEXT     = "#535B62"
TEXT_MUTED = "#727C87"
BORDER   = "#DFE3E5"
BG_PAGE  = "#F4F6F8"
BG_CARD  = "#FFFFFF"
FONT     = "'Ruda',Calibri,sans-serif"
```

When the brand source changes, swap these constants — don't search-and-
replace through the CSS string.

### 2. Coordinate maths

For sections with inline SVG charts, define:

```python
PLOT_X_LEFT  = 44.0
PLOT_X_RIGHT = 800.0
PLOT_Y_TOP   = 16.0
PLOT_Y_BOT   = 170.0

def x_for_index(i, n): ...
def y_for_value(v, y_max): ...
def compute_y_max(rows): ...
```

These are the same primitives every section uses. They live in
`chart_helper.py` if you want to share — see `assets/chart_helper.py`
for a starter.

### 3. Commentary renderer

```python
def render_commentary(auto, user_verbatim):
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
```

This is **the verbatim rule encoded in code**. The renderer only escapes
HTML special characters. It does not paraphrase. It does not strip em
dashes. It does not "fix" capitalisation. The running Claude must hold
the same line in the conversation.

### 4. KPI cards

Inline-styled cards inside a `.ks` flex row. Each `.kc` has a top border
in an accent colour, an uppercase label, a large value, and a sub-label.

### 5. Chart (optional)

Inline SVG only. Gridlines, axes, data series, axis labels. No
`<script>`, no `<canvas>`.

### 6. Scoped CSS

Every selector prefixed `#section-{N}`. Include the standard zones
(`.shb`, `.shl`, `.sc`, `.sn`, `.cmtb`, `.add-note`, `.ks`, `.kc`,
`.kl`, `.kv`, `.ks2`, `.chart-wrap`, `.src`).

### 7. Fragment builder

Pulls it all together. Returns one big f-string. No external templates.

## Page-fill guidance

Section is one logical page. After rendering the preview, look at the
PDF:

- **Underfill** (white gap at bottom) — increase table rows, lower the
  HAVING threshold, or add a chart between the KPI cards and table.
- **Overflow** (content runs onto page 2) — reduce TOP N in the
  breakdown query, tighten row padding from 6px to 5px, or cap chart
  height.

Most sections settle into a stable layout after one or two iterations
during workflow A. Once stable, future runs Just Work.

## Naming conventions

- Section slug: `kebab-case`, descriptive, stable. E.g. `credit-note-analysis`.
- View name: `vw_<PascalCase>`. E.g. `vw_InvoiceCreditNoteStatus`.
- Section number: a stable integer, used in `#section-{N}` and in the
  fragment filename. Numbers don't have to be contiguous.
- Fragment filename: `{period}-section-{N}.html`. The assembler reads
  them in numeric order regardless of the slug.

## When to deviate

The standard anatomy fits ~90% of sections. If one genuinely needs
something different — a two-page layout, an embedded image, multiple
data sources — document the deviation in the SKILL.md so the assembler
and QA scripts know what to expect. The Aged Debtors section is an
example: it forces a page break inside the section so the summary table
and recovery cards never share a page.
