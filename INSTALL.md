# Installation

This is a Claude skill package. Drop the `datasights-monthly-report/`
folder into wherever your environment loads skills from — typically a
`skills/` directory at the project root, or `~/.claude/skills/` for
user-level skills.

The skill's entry point is `SKILL.md`. Read that first if you want to
understand what the skill does and how to use it.

## Dependencies

The Python scripts under `scripts/` use only the standard library
**except** `assemble_report.py`, which optionally imports
[WeasyPrint](https://weasyprint.org) to render the assembled HTML to PDF.

If WeasyPrint isn't installed the assembler still works — it just emits
the HTML and prints a notice instead of writing a PDF. Install with:

```bash
pip install -r requirements.txt
```

WeasyPrint has system-level dependencies on Linux (Pango, GLib, etc.).
On Ubuntu/Debian:

```bash
sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0
```

On macOS with Homebrew:

```bash
brew install pango
```

On Windows, install the GTK3 runtime — see the
[WeasyPrint installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html).

## Required MCP server

The skill assumes the **dataSights** MCP server is connected in the
Claude environment running it. If your data lives elsewhere (a Postgres
warehouse, a Google Sheet, a SaaS API), the patterns in this skill still
apply, but you'll need to swap the `dataSights:query` and
`dataSights:create_report_view` calls referenced in the section
workflow docs for calls to your own MCP tools. The renderers and
assembler don't touch the MCP layer — they consume JSON files written
by Claude — so they don't need any change.

## First-time setup

1. **Install** by placing this folder where your skill loader expects.
2. **Connect dataSights** (or your equivalent MCP server).
3. **Configure brand:**
   - If you already have a brand skill (e.g. `acme-brand`), the running
     Claude will discover it automatically — see
     `references/brand-config.md`.
   - Otherwise, copy `assets/brand.example.json` to a working directory
     (e.g. `reports/brand.json`), edit the colours/fonts/logo path,
     and pass it to the assembler with `--brand-json`.
4. **Run** by asking Claude something like "run the monthly report" or
   "add a section to the monthly report". Claude will read `SKILL.md`
   and walk you through the rest.

## What you'll create on first use

The first run will create:

- `sections/` — one folder per report section, each with a `SKILL.md`
  (workflow doc) and `renderer.py` (Python renderer).
- `reports/` — output directory:
  - `reports/fragments/` — intermediate JSON files (query results) and
    rendered section HTML fragments.
  - `reports/{period}-report-inputs.json` — human-authored content
    (key insights, cross-team asks, action items) for this month.
  - `reports/{period}-{report-slug}.html` and `.pdf` — the final
    assembled report. The `{report-slug}` derives from `brand.report.title`.
  - `reports/{period}-report-actions.json` — carry-forward state read
    by next month's run.

Workflow A in `SKILL.md` walks through designing a section. Workflow B
walks through running the monthly report.

## Updating the skill

The skill is self-contained. To update, replace the folder with a newer
version. No state lives inside the skill — your sections, brand config,
and report outputs live in your working directory.

If you've extended `assets/chart_helper.py` or modified any of the
scripts, save your local edits before replacing the folder.

## Uninstall

Delete the folder. The report outputs and section folders you created
in your working directory are independent and remain.
