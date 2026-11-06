---
name: house-style
description: Make documents in the house style - a PDF (a checklist or packing list, an itinerary or day plan, a one-page report or summary, a comparison of options) or a spreadsheet (a budget, a split, a tracker) - from a layout, filled with the content and drawn in the deployment's name, font, ink and accent. Use it whenever a reply should be a file to keep, print or share, instead of laying the page out by hand.
license: Apache-2.0
compatibility: Runs in the skill computer of the documents environment (traceflow-skill-runtime), which has Chromium (Playwright), openpyxl, pypdf and pypdfium2. Needs no network for its bundled fonts; another font comes from Google Fonts when the computer is online.
metadata:
  icon: icon.svg
  author: traceflow
  traceflow:
    tools: [execute, write_file, read_file, view_image, show_file]
    styles: [pdf, xlsx]
    requires:
      env: [HOUSE_NAME, HOUSE_WORDMARK, HOUSE_FONT, HOUSE_INK, HOUSE_ACCENT]
---

# Documents in the house style

You write what a document says; the house decides how it looks. Every document made here shares one page, one type
scale, one ink and one accent, set by the deployment (its settings, below), so a packing list, a plan and a budget
look like they came from the same place. Never style a document yourself: no colours, fonts or CSS of your own.

## Making one

1. Pick the layout that fits (below) and read it: `read_file` on `.skills/house-style/layouts/<name>.json`.
2. Write your document as the same JSON, its content changed: `write_file` to `document.json`.
3. Draw it:
   - a PDF: `python3 .skills/house-style/scripts/render_pdf.py document.json "Gozo packing list.pdf"`
   - a spreadsheet: `python3 .skills/house-style/scripts/render_xlsx.py budget.json "Sicily budget.xlsx"`. It works
     out every formula itself and says how many; don't recalculate it again with another skill's script.
4. Look before you hand it over: `python3 .skills/house-style/scripts/preview.py "Gozo packing list.pdf" page.png`,
   then `view_image` page.png. Fix what you see (a one-pager that ran onto a second page: shorten it), draw again.
5. Hand it over with `show_file`, and say in one line what it is. Name the file as people read it, with spaces.

## Layouts

**Checklist** ([checklist](layouts/checklist.json)): things to have or do. Sections of 3–6 items, two columns, one
note at the end for the thing not to forget.

**Itinerary** ([itinerary](layouts/itinerary.json)): where to be and when. A section per day, a row per stop: its
time, what it is, one line of detail. Highlight the one thing that can't be missed (a last ferry, a check-in).

**Report** ([report](layouts/report.json)): findings or numbers on one page. Up to four figures, the short of it in a
sentence or two, a bar per part, one thing worth doing.

**Comparison** ([comparison](layouts/comparison.json)): two to four options on one measure. Each option's figure and
a few facts side by side, the best one tagged, the verdict in a sentence, and where the numbers came from.

**Budget** ([budget](layouts/budget.json)): numbers someone will change and watch add up, as a spreadsheet. Inputs
listed in each row's `inputs`, totals as formulas, the total row marked `"total": true`.

## The blocks a PDF is made of

`blocks` is a list; each has a `type`:

- `checklist`: `sections` of `{title, items}`; `columns` 2 (or 1 for a long single list).
- `schedule`: `days` of `{title, note, items: [{time, title, detail, highlight}]}`.
- `figures`: `items` of `{value, label}`, up to four.
- `bars`: `title`, `unit`, `items` of `{label, value, shown?, best?}`.
- `compare`: `options` of `{name, figure, unit, rows: [[fact, value]], best, tag}`; `verdict`.
- `table`: `title`, `columns` of `{label, numeric}`, `rows` of cells.
- `text`, `note` (`label`, `text`), `heading`, `source`.

In any words, `**bold**` is bold and `==words==` is highlighted in the accent: highlight one thing per page at most.

## Writing the content

- Titles say the point, in sentence case: "Pack light, bring layers", not "Packing List".
- The lede is one plain line of what this is for. `for` is the person's first name; `date` today's, as YYYY-MM-DD.
- Short items, no full stops in lists, numbers as people say them (€126–175, 6 km, 10–20 minutes).
- Real facts only; where numbers came from goes in a `source` block.

## The house (settings)

The deployment sets these, once, as the skill's settings: each needs a value, and `default` keeps the default. You
never set or mention them.

| Setting | What it is | Default |
|---|---|---|
| `HOUSE_NAME` | who documents are made by: the header and "Made with …" | traceflow |
| `HOUSE_WORDMARK` | the name's mark, as inline SVG | the name, set in type |
| `HOUSE_FONT` | the font family: one bundled (Inter, Instrument Sans, IBM Plex Sans, Source Serif 4, all OFL, in `assets/fonts`), else from Google Fonts when online | Inter |
| `HOUSE_INK` | the darkest colour; every grey is mixed from it | #18181B |
| `HOUSE_ACCENT` | the one accent: the highlight, the best tag, the answer cell | #E4E4E7 |
