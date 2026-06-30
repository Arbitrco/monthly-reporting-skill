# Pagination QA

Every assembled report must be rasterised and visually inspected before
delivery. Pagination bugs are common and not catchable from HTML alone —
WeasyPrint sometimes splits content in places that look fine in a browser.

```bash
python scripts/qa_pages.py \
  --pdf reports/{period}-{report-slug}.pdf \
  --out reports/preview/
```

This produces one JPEG per page in `reports/preview/`. View each one
before delivery.

## What to look for

| Item | Bad | Fix |
|---|---|---|
| Each section starts on its own page | Page begins with the bottom half of one section and the top of the next | Check the section has `page-break-before: always` in its scoped CSS |
| No orphan headers | Section header on the last line of a page with content on the next | Wrap the orphan header + first content block in `break-inside: avoid` |
| No large bottom gap | More than ~0.5 inches of empty space below the section | Section is under-filled — see below |
| No overflow onto an extra page | Section content spilling onto a page with only a footer | Section is over-filled — see below |
| Headers + footers on every content page | Either missing on a section page | Check the running-header CSS (`.shb { position: running(section-header) }`) — see `assembler.md` |
| Brand colours render correctly | Greyed out, wrong hex, fallback colour | CSS variable failed or brand value not propagated — re-run with explicit `--brand-json` |
| Cover page has no global footer overlay | Navy bar appears at the bottom of the cover | The `@page` margin: 0 rule isn't being applied to the cover. Check the cover div has no `class="page-content"` or `[id^="section-"]` |

## Standard fixes for under-fill

The section is one logical page. Fix in the section's `renderer.py`,
not the assembler:

| Symptom | Fix |
|---|---|
| Big white gap below a table | Raise `TOP N` in the breakdown query, lower a HAVING threshold |
| Commentary block small relative to gap | Don't truncate user commentary; let it run |
| KPI cards stranded with empty space below | Add a chart between cards and breakdown, or split the breakdown into two side-by-side tables |

## Standard fixes for over-fill

| Symptom | Fix |
|---|---|
| Table runs onto page 2 | Reduce `TOP N`, or trim row padding from 6px to 5px |
| Commentary too long | Cap at two paragraphs of ~80 words each in your draft; the user's verbatim text is *not* capped (don't paraphrase) |
| KPI cards wrap to two rows | Reduce font sizes by 1pt, or drop one card |
| Chart pushes content off page | Cap chart height to 2.0in |

## Re-running after a fix

1. Edit the section's `renderer.py` (or the section's SKILL.md if the
   query needs adjustment).
2. Re-run the section's renderer with the existing rows JSON. No need
   to re-query unless the SQL changed.
3. Re-run `assemble_report.py`.
4. Re-run `qa_pages.py`.

Do not edit the assembled `report.html` directly — those edits are lost
on the next assembly run.

## When the fix is in the assembler

Rare. If every section overflows or every section has a wrong-coloured
header, the bug is in `scripts/assemble_report.py` (probably brand CSS,
page-break rules, or the running-header mechanic).

Diagnose carefully before changing the assembler — one mis-edit there
breaks every section. Test by running against a known-good month's
inputs and diffing the HTML output.

## Two-page sections

Some sections are designed to span two pages — e.g. an Aged Debtors
section, where a summary table sits on page 1
and per-debtor recovery cards sit on page 2. These sections force an
internal page break:

```css
#section-7 .notes-hd {
  page-break-before: always;
  break-before: always;
}
```

When QA'ing a two-page section, both pages should have the running
header at the top and the global footer at the bottom. The running
header repeats automatically; if it doesn't, check that the section's
`.shb` has `position: running(section-header)` set (it should — that's
in the section's scoped CSS).

## Cover page checks

The cover is special — it's the only page that uses the default `@page`
rule (margin 0, no global footer). When QA'ing the cover:

- No navy footer band at the bottom — the cover has its own white
  footer.
- Decorative motif shapes appear in the corners.
- Period, Issued, Data-as-at meta line is present and the dates are
  correct.
- The company logo is embedded (not a broken-image icon).

If the global footer appears on the cover, the cover div has accidentally
matched the `[id^="section-"]` selector — check that its id is `cover`,
not `section-0`.
