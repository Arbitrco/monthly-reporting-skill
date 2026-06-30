# The assembler

`scripts/assemble_report.py` is the orchestrator. It runs at the end of
workflow B step B7 and produces the final HTML and PDF.

Most of the time you don't need to read this — the assembler Just Works
once the inputs JSON and fragments exist. Read this when:

- The assembler exits with an error.
- A new section is being added and the assembler needs to know about it.
- Pagination is misbehaving and you need to understand the running
  header / global footer mechanics.

## What it does

1. Reads `reports/{period}-report-inputs.json` (cover metadata + Key
   Insights + Cross-Team Asks + Action Items).
2. Loads brand constants from the brand source (skill, JSON, or
   defaults — see `brand-config.md`).
3. Builds the outer HTML document with the brand CSS, running header,
   and global footer.
4. Builds the cover page (navy, with decorative motifs and embedded
   logo).
5. Builds Section 1 (Key Insights and Decisions Required) inline from
   `insights[]`.
6. Reads each `reports/fragments/{period}-section-{N}.html` in numeric
   order, normalises it (see below), and concatenates into the body.
7. Builds the Cross-Team Asks and Action Items table sections inline
   from `cross_team_asks[]` and `action_items[]`.
8. Appends the global footer div.
9. Writes `reports/{period}-{report-slug}.html`. The slug is derived
   from `brand.report.title` — "Monthly Operational Report" becomes
   `monthly-operational-report`. Override with `--out-html`.
10. Renders to PDF via WeasyPrint.
11. Writes `reports/{period}-report-actions.json` for next month's
    carry-forward.

## The fragment normaliser

Section renderers shouldn't all need to be edited if the report shell
evolves. The assembler accepts fragments in slightly different shapes
and normalises them:

| Problem | Fix |
|---|---|
| Fragment is a full `<!DOCTYPE html>...</html>` doc | Strip wrapper, hoist `<style>` blocks, keep `<body>` content |
| Fragment has legacy `.shm/.mp/.mr` right-side metadata | Strip those divs |
| Fragment has `.shb` but no `.shl` logo box | Inject the brand logo box before `.shb`'s closing tag |
| Fragment `.shb` has old padding `padding:14px 48px` | Rewrite to `padding:0 48px;height:56px` |

Logo injection is **nesting-aware**: it finds the closing tag of the
`.shb` div by tracking opener/closer depth, not by greedy regex. This
matters because section CSS sometimes contains nested divs inside the
header bar.

The normaliser is idempotent — running it twice on the same fragment
produces the same output. Sections that emit correctly-formed `.shl`
boxes themselves pass through unchanged.

## Page break and running header mechanics

This is the trickiest part of the assembler. The setup uses WeasyPrint's
`@page` named pages plus a running element to produce a section header
that automatically follows the section across page breaks.

### Two `@page` rules

```css
/* Cover: full bleed, no margins, no running header */
@page { size: letter; margin: 0; }

/* Content pages: reserve top space for the running header
   and bottom space for the global footer. */
@page content-page {
  size: letter;
  margin: 0.78in 0 0.50in 0;
  @top-center {
    content: element(section-header);
    width: 8.5in;
    height: 0.78in;
    padding: 0;
  }
}

/* Bind every section's outer div to the content-page rule. */
.page-content, [id^="section-"] { page: content-page; }
```

### Running header

```css
.shb { position: running(section-header); }
```

Every section's `.shb` is hoisted out of normal flow into the named
running element `section-header`. When a new section's `.shb` enters
the page, it replaces the running element — so the header always
matches the current section across page breaks.

This means **the section's `.shb` is rendered by `@top-center` in the
page margin, not in document body flow.** When a section is two pages
long, the second page automatically gets a copy of the same header.

### Global footer

The footer uses a fixed-position div with a negative bottom offset:

```css
#global-footer {
  position: fixed;
  bottom: -0.50in;
  /* ...navy band styling... */
}
```

The `@page content-page` margin reserves 0.50in at the bottom. The
footer's `bottom: -0.50in` pushes it into that reserved margin area, so
it renders at the page bottom on every content page.

On the cover page, `@page` has `margin: 0`, so the footer's `bottom:
-0.50in` puts it off-page where it's hidden — letting the cover's own
white footer bar show.

This dual mechanism (reserve margin + offset into margin) is the only
reliable way to get a repeating footer in WeasyPrint that doesn't
overlap content and doesn't appear on the cover.

### Pagination control

Visual blocks that should never split across pages get
`break-inside: avoid; page-break-inside: avoid`:

```css
.chart-card, .chart-wrap, .kpi-grid, .kpi, .ks,
.callout, .cmtb, .sn, .vtw, svg {
  break-inside: avoid;
  page-break-inside: avoid;
}
```

Tables may still break by row, but rows themselves don't split:

```css
thead { display: table-header-group; }
tr { break-inside: avoid; page-break-inside: avoid; }
```

`display: table-header-group` makes the table header repeat on each
page if a table spans multiple pages.

## CLI flags

```
python scripts/assemble_report.py --period YYYY-MM
                                  [--issued "DD Month YYYY"]
                                  [--data-as-at "DD Month YYYY"]
                                  [--brand-skill PATH | --brand-json PATH]
                                  [--inputs PATH]
                                  [--fragments-dir PATH]
                                  [--out-html PATH]
                                  [--out-pdf PATH]
                                  [--out-actions PATH]
```

Defaults follow the working-directory layout in the parent SKILL.md.

## What if a fragment is missing?

The assembler doesn't fail — it inserts a placeholder div with a
"Fragment not found" message in the section's slot. The build still
produces a PDF so the user can see which sections rendered and which
didn't.

If you intentionally want to skip a section this month, leave the
fragment file absent — the placeholder is intentional and visible.

## What if the inputs file is missing?

The assembler fails loudly. The inputs file is mandatory because it
contains the cover metadata and the human-authored sections, none of
which the assembler can synthesise.

## When to modify the assembler

Modify it when you're adding new global structure (a new front-matter
section between cover and Key Insights, a new appendix at the back).
Don't modify it for section-specific changes — those live in the
section's `renderer.py`.

Test changes by running an assembly against a known-good month and
diffing the HTML output. The brand CSS, running-header, and footer
mechanics are easy to break and hard to debug from a PDF alone.
