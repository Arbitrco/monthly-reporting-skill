# Inputs JSON and carry-forward actions JSON

The report has two persistent JSON files:

| File | Purpose | Written by |
|---|---|---|
| `reports/{period}-report-inputs.json` | Human-authored content for this month (Key Insights, Cross-Team Asks, Action Items, cover metadata) | The running Claude in workflow B step B6 |
| `reports/{period}-report-actions.json` | Carry-forward state for next month — open + closed items | The assembler at the end of workflow B |

Both are consumed by the assembler. The inputs file drives this month's
output; the prior month's actions file feeds carry-forward decisions in
B3.

## `{period}-report-inputs.json`

Schema:

```json
{
  "period":       "2026-04",
  "period_label": "April 2026",
  "issued":       "20 May 2026",
  "data_as_at":   "20 May 2026",
  "insights": [
    { "kind": "insight",
      "label": "Revenue trend",
      "text":  "Revenue held flat versus March at $X.Xm, in line with the trailing 12-month average." },
    { "kind": "decision",
      "label": "Pricing review",
      "text":  "Customer X has been at 32% credit rate for three months. Recommend pricing review and scope documentation rework. Decision needed at the next OLT meeting." }
  ],
  "cross_team_asks": [
    { "dept":    "Sales",
      "request": "Confirm whether the renewal pipeline for May includes the Acme account.",
      "by_when": "30 May 2026" }
  ],
  "action_items": [
    { "owner":   "Finance",
      "action":  "Run a scope-review session with the billing team for Customer X.",
      "by_when": "31 May 2026" }
  ]
}
```

### Field rules

- **`period`** — `YYYY-MM`. Must match the `--period` flag passed to the
  assembler.
- **`period_label`** — Human-readable, e.g. `"April 2026"`. Used on the
  cover and in headers.
- **`issued`** — Date the report is issued. Default: today. Override
  with the assembler's `--issued` flag if needed.
- **`data_as_at`** — Date the underlying data was sourced. Often the
  Xero sync date. Defaults to `issued`.
- **`insights[]`** — Section 1 items.
  - `kind: "decision"` → renders with the alert-coloured border and the
    "Decision Required:" label prefix.
  - `kind: "insight"` → renders with the accent-coloured border and
    just the label.
  - `label` — short title in title case.
  - `text` — full prose. Plain text, no inline HTML.
- **`cross_team_asks[]`** — Section 9 rows. `dept`, `request`, `by_when`.
  Empty array `[]` triggers the assembler's empty-state card.
- **`action_items[]`** — Section 10 rows. `owner`, `action`, `by_when`.
  Empty array `[]` triggers the empty-state card.

### Writing the file

In workflow B step B6:

1. Gather insights, asks, items from the user in B5.
2. Build the dict in Python or write the JSON directly.
3. Save to `reports/{period}-report-inputs.json` with `indent=2` and
   `ensure_ascii=False`.
4. Validate by reading it back as JSON before calling the assembler.

If the file is malformed the assembler exits with an error; fix the
inputs and re-run.

## `{period}-report-actions.json`

Schema:

```json
{
  "period":    "April 2026",
  "generated": "2026-05-20",
  "cross_team_asks": [
    { "dept":    "Sales",
      "request": "...",
      "by_when": "30 May 2026",
      "status":  "open" }
  ],
  "action_items": [
    { "owner":   "Finance",
      "action":  "...",
      "by_when": "31 May 2026",
      "status":  "open" },
    { "owner":   "Operations",
      "action":  "...",
      "by_when": "30 April 2026",
      "status":  "closed",
      "closed_period": "April 2026",
      "closed_note":   "Completed — billing template updated." }
  ]
}
```

The assembler writes this file at the end of every run. Every item from
the inputs JSON appears here. Items the user marks "resolved" in the
next month's run get `status: "closed"` and `closed_period` populated
when that next month's run completes.

### Status values

| Status | Meaning |
|---|---|
| `open` | Still outstanding. Will appear on next month's carry-forward list. |
| `closed` | Done. Stays in the file for audit but doesn't appear in any rendered section. |

### The carry-forward conversation

In workflow B step B3, you read **the most recent prior** actions file
(not this month's — that doesn't exist yet). You present the **open**
items to the user. For each, they say one of:

- **resolved** — change status to `closed`, set `closed_period` to this
  month's label, optionally capture a closing note. **Do not include in
  this month's rendered Sections 9/10.**
- **carry forward** — include in this month's rendered Sections 9/10
  with the original text, or with the user's updated wording/date.
- **remove** — drop entirely. This is a destructive operation;
  double-check with the user before doing it.

The user may also say "all carry forward" to keep everything as-is.

In workflow B step B5, you ask about **new** items. New items get
appended to the lists alongside any carried-forward items.

### Why two files

- **inputs.json** is what *the user authored this month*. It's the
  source of truth for this month's rendered report.
- **actions.json** is the *audit trail*. It contains everything ever
  raised, with status. Future runs read it to know what's still open.

The two files have different shapes deliberately — inputs has cover
metadata + insights that don't carry forward; actions has only the
status-tracked items.

## Empty-state language

If a list is empty in the inputs JSON, the assembler renders a polite
empty-state card instead of the table. Default text:

| Section | Empty-state text |
|---|---|
| Cross-Team Asks | "No cross-team asks have been raised this month. Outstanding items from prior reports remain in their respective owners' workstreams." |
| Action Items | "No new action items have been raised from this month's results. Decisions flagged in Section 1 carry their own owners; standing operational tasks remain in the team trackers." |

The text is encoded in `assemble_report.py`. Override by passing
`--empty-cross-team "..."` / `--empty-actions "..."` if you want
different wording.

## Don't ask the user to write JSON

The user interacts in natural language. All JSON manipulation happens
via the skill on their behalf. If you find yourself pasting JSON
snippets into the conversation, simplify.
