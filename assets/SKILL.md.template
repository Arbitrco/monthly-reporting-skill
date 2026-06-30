---
name: {{SECTION_SLUG}}
description: >
  Generates the {{SECTION_TITLE}} section for the monthly operational report.
  [REPLACE: one-sentence summary of what the section shows and what it
  helps the reader understand.]
  Use this skill whenever a monthly report needs [REPLACE: 3-5 synonyms
  or related concepts]. Triggers include "add the {{SECTION_SLUG}} section",
  "include {{SECTION_TITLE}}", "run {{SECTION_TITLE}} analysis", or any
  request to report on [REPLACE: topic domain in plain language]. Always
  use this skill rather than writing ad-hoc queries.
compatibility: >
  Requires dataSights:query. HTML output produced by
  sections/{{SECTION_SLUG}}/renderer.py.
---

# {{SECTION_TITLE}} — monthly reporting skill

Generates Section {{SECTION_NUMBER}} of the operational monthly report.
Pulls live data from `{{VIEW_NAME}}`, saves the rows to JSON, hands them
to the renderer, and produces a self-contained HTML fragment with KPI
cards, [REPLACE: inline SVG charts / table / both], and commentary.

The renderer lives at `sections/{{SECTION_SLUG}}/renderer.py`. All HTML
structure, scoped CSS, SVG coordinate maths, and colour mapping are
encoded there. This markdown defines the data inputs, narrative rules,
and workflow.

---

## Background & logic

[REPLACE: one paragraph describing what this section measures, what
business question it answers, and any non-obvious context the reader
needs. Include any baked-in filters (e.g. "excludes EOM-dated invoices
which are a known batch artefact") and explain why.]

---

## Step 1 — Determine the reporting period

[REPLACE: state the period rule. Choose one of:
- Trailing 12 months ending at the reporting month.
- Single month = the reporting month.
- Current financial year YTD through reporting month.
- Rolling 13 months for a trend chart.
- Other — describe.]

**Reporting month convention:** the last fully completed calendar month.
If today is 18 May 2026, the reporting month is April 2026.

Parametric form:

```
[REPLACE: derivation expression]
```

Worked example (April 2026 reporting month):

- `[var1]` = `[value]`
- `[var2]` = `[value]`

---

## Step 2 — Run the query and save as JSON

Run the following query and save the result rows to
`reports/fragments/{period}-section-{{SECTION_NUMBER}}-rows.json`.

```sql
[REPLACE: SQL query against {{VIEW_NAME}}. Single SELECT. No joins —
joins live in the view.]
```

Each row should include these columns (the renderer reads them directly):

| Column | Use |
|---|---|
| `[col1]` | [purpose] |
| `[col2]` | [purpose] |

[Optional second query — only if the section needs both headline +
breakdown data:]

```sql
[REPLACE: second query]
```

Save the result as:

```json
{
  "[top-level-key]": [
    { "col1": ..., "col2": ... },
    ...
  ]
}
```

Or use multiple top-level keys if the section needs both headline
summary and a per-row breakdown.

---

## Step 3 — Render a preview fragment (no commentary)

Run the renderer with no commentary flags to produce a preview the user
can review before authoring commentary:

```bash
python sections/{{SECTION_SLUG}}/renderer.py \
  --rows   reports/fragments/{period}-section-{{SECTION_NUMBER}}-rows.json \
  --period "April 2026" \
  --output reports/fragments/{period}-section-{{SECTION_NUMBER}}.html
```

The renderer emits:
- A scoped `#section-{{SECTION_NUMBER}}` CSS block.
- The standard `.shb` navy header bar (the assembler will inject the
  logo box at assembly time).
- A scope note (`.sn`).
- [REPLACE: KPI cards / chart / table — describe what's in the preview.]
- A source note (`.src`).

Preview the output in chat or via `present_files` before continuing.

---

## Step 4 — Author the auto-narrative

Write 2–3 short paragraphs based on the current period's data.

[REPLACE: pattern-keyed phrasings — e.g.

- **[pattern A] — [trigger condition]** — [what to say: lead metric,
  comparison, action].
- **[pattern B] — [trigger condition]** — [same shape].
]

Standard interpretive notes:

- [REPLACE pattern 1: what it usually means]
- [REPLACE pattern 2: what it usually means]
- [REPLACE pattern 3: what it usually means]

**Em dashes:** if the brand style disallows em dashes, use colons or
rewrite. The verbatim rule below means this applies to your auto-commentary
*only* — the user's text is rendered exactly as given.

---

## Step 5 — Collect user commentary

Ask:

> "[REPLACE: one-line prompt tailored to this section. Example:
> 'Is there anything you'd like to add to the [topic] commentary — for
> example, context on [common factor], a process change underway, or any
> note for the reader? If not, the auto-generated commentary will stand
> on its own.']"

Wait for the response.

**Render verbatim.** The user's text is passed to the renderer as
`--user-commentary "..."` (or `--user-commentary-file path.txt` for
long input) exactly as written. The renderer HTML-escapes the text and
inserts it into the `.add-note` sub-block under "Additional notes"
without any other transformation.

**Do not:** paraphrase, summarise, reword, correct typos, expand
abbreviations, replace punctuation. See `commentary-verbatim.md` in
the parent meta-skill.

If the user says they have no commentary, omit the `--user-commentary`
flag.

---

## Step 6 — Re-render with both commentary fields

```bash
python sections/{{SECTION_SLUG}}/renderer.py \
  --rows            reports/fragments/{period}-section-{{SECTION_NUMBER}}-rows.json \
  --period          "April 2026" \
  --output          reports/fragments/{period}-section-{{SECTION_NUMBER}}.html \
  --auto-commentary "Paragraph 1.

Paragraph 2." \
  --user-commentary "<the user's text exactly as written>"
```

Use double newlines (a blank line) inside `--auto-commentary` to create
multiple paragraphs.

---

## Step 7 — QA before delivering

- [ ] Visually inspected the rendered fragment — no large white gap,
      no overflow onto a second page.
- [ ] [REPLACE: a section-specific QA check — e.g. "Headline KPI looks
      sensible given the prior month."]
- [ ] [REPLACE: another section-specific check — e.g. "Sync rate above 90%."]
- [ ] No em dashes in the auto-commentary.
- [ ] User commentary rendered character-for-character.
- [ ] All section labels in ALL CAPS.
- [ ] Brand colours render correctly.

---

## Output contract

The renderer writes a self-contained fragment to the `--output` path. It:

- Starts with `<div class="report-section" id="section-{{SECTION_NUMBER}}">` and ends with `</div>`.
- Has no outer `<!DOCTYPE>`, `<html>`, `<head>`, or `<body>` tags.
- Includes a scoped `<style>` block (every selector prefixed with `#section-{{SECTION_NUMBER}}`).
- Uses inline SVG only — no `<canvas>`, no `<script>`, no Chart.js.
- Declares `page-break-before: always` on `#section-{{SECTION_NUMBER}}`
  so the section starts on a new PDF page.
- Omits any in-flow footer (the assembler adds a single global footer).
- Omits the `.shl` logo box — the assembler injects the brand logo into
  the header at assembly time.

---

## View dependency

```
{{VIEW_NAME}}
└── [REPLACE: list of underlying tables / views joined inside this view]
```

Do not delete or rename `{{VIEW_NAME}}` while this skill is in use.

---

## Drill-down queries (for follow-up during commentary gathering)

Useful ad-hoc queries against the same view that the report does not
include but that the user may ask for.

```sql
-- [REPLACE: describe what this drill-down answers]
SELECT
    [REPLACE]
FROM {{VIEW_NAME}}
WHERE [REPLACE]
ORDER BY [REPLACE]
```

---

## SVG geometry (reference only — encoded in renderer.py)

For reviewers and anyone extending the renderer:

- ViewBox: `0 0 [W] [H]`. Plot area: x `[L]`–`[R]`, y `[T]`–`[B]`.
- Y-axis scale: [REPLACE].
- X positions: [REPLACE].
- Series colour map: [REPLACE].

---

## Known limitations

- [REPLACE: any known quirks of the data or rendering — e.g. "View
  exposes percentages to 1dp only", "Most recent 1-2 months may lag
  because credit notes trail invoices by 2-4 weeks"].
