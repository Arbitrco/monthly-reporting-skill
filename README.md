# datasights-monthly-report

A Claude [skill][skills] for building and running recurring branded monthly
operational reports. Pulls data via the [dataSights][datasights] MCP server,
gathers human commentary alongside an auto-generated draft, and assembles a
self-contained branded HTML + PDF with a cover page, section fragments, and
a global footer.

This skill was extracted from a production monthly finance report pattern
and generalised so other teams can fork it and bend it to their own data,
brand, and section mix.

> **This is a community skill, not an official Anthropic product.** It uses
> Anthropic's Claude skill format but is not endorsed or maintained by
> Anthropic.

## What it does

Two workflows, both inside the skill:

**A. Design a new section** — define one new topic for the report. Picks a
dataSights view, scaffolds a workflow doc (`SKILL.md`) plus a Python
renderer (`renderer.py`) into `sections/<slug>/`. You fill in the SQL,
KPI definitions, and commentary guidance.

**B. Run the monthly report** — every month, in turn:

1. Confirm the reporting period and check data sync status.
2. Load open items from last month's report (carry-forward).
3. For each section: query → save rows JSON → render preview → present
   data → draft auto-commentary → ask the user for their commentary →
   re-render with both. **User commentary is rendered verbatim** — no
   paraphrasing, typo correction, or punctuation substitution.
4. Capture human-authored sections (Key Insights, Cross-Team Asks,
   Action Items).
5. Run the assembler. Output: `reports/{period}-{report-slug}.html` and
   `.pdf`, plus a carry-forward actions file for next month.

The whole pipeline is intermediate-JSON-based: query results, rendered
fragments, and the human-authored content all live as files in the
working directory. Re-rendering doesn't re-query.

## Quick start

```bash
git clone https://github.com/<you>/datasights-monthly-report.git
cd datasights-monthly-report
pip install -r requirements.txt   # WeasyPrint + system deps for PDF
```

Drop the folder where your environment loads Claude skills from
(typically `~/.claude/skills/` or a project-level `skills/` directory).
Then in Claude, ask:

- _"Add a new section to the monthly report"_ → walks you through
  workflow A.
- _"Run the monthly report for [Month YYYY]"_ → walks you through
  workflow B.

Full setup notes, including WeasyPrint system dependencies and brand
configuration, are in [`INSTALL.md`](INSTALL.md). The skill's full
operating manual (what Claude reads when triggered) is in
[`SKILL.md`](SKILL.md).

## Requirements

- **Python 3.10+** for the scripts. Standard library only, except:
- **WeasyPrint** (`pip install -r requirements.txt`) for HTML → PDF.
  The assembler still produces HTML without it.
- **dataSights MCP server** connected in the Claude environment.
  If your data lives elsewhere (Postgres, BigQuery, an API), the
  patterns transfer but you'll need to swap the `dataSights:query` calls
  in section workflow docs for calls to your MCP server.
- **Claude with the skills system enabled** (Claude.ai, Claude Code, or
  another Claude environment that loads skills).

## What's in the box

```
datasights-monthly-report/
├── SKILL.md                ← skill entry point — Claude reads this first
├── INSTALL.md              ← setup notes
├── README.md               ← this file
├── LICENSE                 ← MIT
├── requirements.txt
├── references/             ← deep-dive docs Claude pulls in as needed
│   ├── assembler.md
│   ├── brand-config.md
│   ├── commentary-verbatim.md
│   ├── inputs-json.md
│   ├── pagination-qa.md
│   └── section-anatomy.md
├── scripts/                ← executable Python
│   ├── assemble_report.py  ← combines fragments → HTML + PDF + actions JSON
│   ├── new_section.py      ← scaffolds a section (workflow doc + renderer)
│   ├── qa_pages.py         ← PDF → per-page JPEGs for review
│   └── render_pdf.py       ← single-fragment HTML → PDF for QA
├── tests/                  ← stdlib unittest regression tests
│   └── test_assemble.py    ← escaping, dom-ids, period + logo-mime checks
└── assets/
    ├── brand.example.json  ← starter brand config
    ├── chart_helper.py     ← shared inline-SVG primitives
    └── section_template/
        ├── SKILL.md.template
        └── renderer.py.template
```

## Customising for your team

Three things are configurable; the rest of the skill stays as-is:

1. **Brand.** The skill prefers an existing Claude brand skill (looks for
   `*-brand` or `*-design-system` in your environment). Falls back to a
   `brand.json` (see `assets/brand.example.json`). Output filename is
   derived from `brand.report.title` — set this to your report's name and
   the file becomes `{period}-{your-report-slug}.html`.

2. **Sections.** Workflow A in the skill scaffolds new sections. The
   templates in `assets/section_template/` are the seed — edit them in
   your fork if you want different defaults (e.g. different CSS, no
   chart slot, different commentary block layout).

3. **The assembler.** `scripts/assemble_report.py` is where the cover
   page, page-break rules, and global footer live. Edit it if you need
   a different cover layout or a back-of-report appendix.

The section workflow docs (`sections/<slug>/SKILL.md`) and renderers
(`sections/<slug>/renderer.py`) live in **your** working directory, not
in this repo. They're your team's customisation surface.

## Forking and pulling updates

Forks are expected. If you pull upstream changes later, the things most
likely to need a merge:

- `assets/section_template/*.template` (if you edited these in your fork
  AND upstream has changed them)
- `scripts/assemble_report.py` (if you've extended the assembler)
- `references/*.md` (low-impact — these are reference docs Claude reads)

Your sections under `sections/` and your `brand.json` are independent
of this repo and won't conflict.

## Contributing

Issues and PRs welcome. Please:

- Keep changes generic. If a feature only makes sense for one company,
  it doesn't belong upstream — it belongs in a fork.
- Don't add new runtime dependencies without discussion. WeasyPrint is
  the only one and it's optional.
- Preserve the verbatim-commentary rule. It's the most important
  behavioural promise this skill makes.

## License

[MIT](LICENSE) — do what you like, attribution appreciated.

## Acknowledgements

This skill generalises a working production pattern for monthly
operational finance reporting. The original implementation used
[dataSights][datasights] as its data layer, [Xero][xero] as one of the
accounting sources, and [WeasyPrint][weasyprint] for PDF rendering.

[skills]: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview
[datasights]: [https://datasights.co/]
[weasyprint]: https://weasyprint.org
[xero]: https://www.xero.com
