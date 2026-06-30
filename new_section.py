# The verbatim commentary rule

The single most important rule in this skill. When any section collects
free-text commentary from the user, **render it strictly verbatim**.

This applies to every section. It is enforced in the running Claude (you),
not in the renderer scripts (which only HTML-escape).

The same HTML-escaping applies to the human-authored inline sections (Key
Insights, Cross-Team Asks, Action Items): `assemble_report.py` escapes those
values too, so `<`, `>` and `&` in an insight or action render literally
instead of being parsed as markup and silently dropped. You still write those
items verbatim; the assembler only escapes, never rewrites.

The `.add-note` block renders with `white-space: pre-wrap`, so single line
breaks and runs of spaces in the user's text survive into the PDF rather than
being collapsed.

## Do

- Render the user's exact words, character for character.
- Apply HTML escaping only: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`,
  `"` → `&quot;` inside attributes.
- Split into paragraphs only where the user used line breaks in their
  input. Two newlines = paragraph break.

## Do not

- Paraphrase, summarise, restructure, or reword.
- Add connecting phrases, transitions, or scene-setting context.
- Correct typos, capitalisation, or grammar.
- Expand abbreviations or rewrite contractions ("inv" stays "inv",
  not "invoice"; "don't" stays "don't").
- Replace em dashes, ampersands, or other punctuation, even if the
  brand style prefers different punctuation. The brand rule applies
  to auto-commentary; the verbatim rule applies to user commentary.
- Substitute terms ("Bel" stays "Bel", not "Belinda").

## Why it matters

The user wrote what they wrote because that's what they meant. The
report goes to leadership, sometimes to a board. If you "improve" the
user's wording you are putting words in their mouth and they will catch
it. They will lose trust in the system. Once trust is lost they go back
to writing the report by hand.

The auto-commentary (your draft, from the data) is where you exercise
prose judgement. The user commentary block is where they exercise theirs.
Keep them visually separated and keep your hands off the user side.

## Where it shows up in the report

Each section renderer takes both flags:

```bash
--auto-commentary "Your data-driven draft.

  Possibly a second paragraph."
--user-commentary "The user's text, verbatim."
```

The renderer produces:

```html
<div class="cmtb">                          <!-- the commentary block -->
  <p>Your data-driven draft.</p>            <!-- auto-commentary paragraphs -->
  <p>Possibly a second paragraph.</p>

  <div class="add-note">                    <!-- user verbatim sub-block -->
    <span class="lbl">Additional notes</span>
    <p>The user's text, verbatim.</p>
  </div>
</div>
```

Visually the `.add-note` block sits inside `.cmtb` with its own border
and italic styling so a reader can tell at a glance where Claude stopped
writing and where the user started.

## When the user's text is unclear

If the user's commentary contains a typo or ambiguity that materially
changes the meaning, **ask them to clarify** rather than guessing. Do
not silently correct. Examples:

- "Bel chasing X" — ambiguous if there are multiple Bels. Ask.
- "Revenue down by 5%" when the data says 5.2% — they may have intended
  the round figure. Ask once: "The data shows 5.2% — should I use that
  or your wording 5%?"
- A sentence that doesn't parse — ask them to rephrase.

If the typo is obvious and harmless (e.g. "teh" for "the"), still leave
it. The user can see the rendered output and will fix it themselves if
they want to.

## When the user says "no commentary"

Pass an empty string to `--user-commentary` (or omit the flag entirely).
The `.add-note` block is suppressed; only the auto-commentary paragraphs
render.

## Where this rule lives in the workflow

Workflow B step 7: "Ask the user for their commentary. Their text will
be rendered **verbatim** — say so explicitly."

Tell them that line. They'll write more freely if they know you won't
edit them.
