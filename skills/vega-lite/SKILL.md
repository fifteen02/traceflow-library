---
name: vega-lite
description: How to show numbers as a chart with render_vega - when a chart helps and when a sentence is better, which chart answers which question, and a Vega-Lite spec that passes first time (data inline, few colours, one y axis). Use it when the person asks to see, chart, plot, graph, compare or track numbers, a trend, a breakdown or a spread, or when an answer is a handful of numbers worth seeing at once.
license: Apache-2.0
compatibility: render_vega must be offered (the skill isn't offered without it). Its scripts are optional and run in the skill computer of the documents environment (traceflow-skill-runtime, which has python3); vl-convert-python comes from requirements.txt when that computer is built. Needs no internet.
metadata:
  icon: icon.svg
  author: traceflow
  traceflow:
    tools: [render_vega, execute, write_file, view_image]
    requires:
      tools: [traceflow/render_vega@1]
---

# Charts with render_vega

`render_vega` takes `{title?, spec}`: a [Vega-Lite](https://vega.github.io/vega-lite/) spec with its rows inline. traceflow checks it, compiles it, and writes `charts/<slug>.vl.json` and `charts/<slug>.png` in the thread's workspace. The chat app draws the spec live; WhatsApp and the other channels get the PNG. The tool itself, `traceflow/render_vega@1`, is defined in the library's [client-tools/render_vega](https://github.com/fifteen02/traceflow-library/tree/main/client-tools/render_vega), with every example below.

## Always

- **Say the point in one line, then the chart.** "Groceries and eating out are two thirds of this month." The chart shows the rest; never read its numbers back in words.
- **A chart only when it helps.** Two or three numbers are a sentence ("€412 on groceries, €286 eating out"). A chart is for a shape: a trend, a ranking, a share, a spread, more numbers than a sentence holds.
- **The rows go inline** in `data.values`, already summed or averaged to what the chart shows. Never a `url`: nothing is fetched.
- **Titles in words.** An axis says what and in what unit ("Steps a day", "€"); a title, when there is one, says what the chart is of. Set a title to `null` when the labels say it already.
- **One colour for one series.** Colour only to tell series apart, never to decorate.
- **Made-up numbers never.** Chart only what you read or worked out, and say where it came from.

## Which chart for which question

| The question | The chart | Example |
|---|---|---|
| Which is biggest? How do they compare? | Bars, sorted (`"sort": "-x"`), horizontal when labels are long | [bar-by-category](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/good/bar-by-category.json) |
| How has it changed? | A line, time along x in order | [line-over-time](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/good/line-over-time.json) |
| How have a few things changed? | A line each, coloured by series (8 at most) | [lines-by-group](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/good/lines-by-group.json) |
| What share went where? | Stacked bars, normalised (`"stack": "normalize"`) | [stacked-share](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/good/stacked-share.json) |
| How is it spread? What is usual? | A histogram: `bin` on x, `count` on y | [histogram](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/good/histogram.json) |
| Many categories | The largest five, the rest summed as Other | [largest-and-other](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/good/largest-and-other.json) |
| Two measures in different units | Two charts side by side (`hconcat`), never two y axes | [two-measures-side-by-side](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/good/two-measures-side-by-side.json) |
| An average per group | A `transform` (aggregate), then encode what it makes | [with-transform](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/good/with-transform.json) |

A pie (`"mark": "arc"`) only for parts of one whole, 6 slices at most; bars read better almost always.

## The limits render_vega holds you to

- At most **5000 rows**: sum or average them first.
- At most **8 colours**: keep the largest, group the rest as Other.
- A pie of at most **6 slices**.
- **One y axis**: no `"resolve": {"scale": {"y": "independent"}}`.
- Every field an encoding names is in the rows, or made by a `transform` (`as`).
- A `mark` wherever there is an `encoding`, and data in every chart.

## Calling it

```json
{"title": "Spending by category, October",
 "spec": {"data": {"values": [{"category": "Groceries", "euros": 412}, {"category": "Eating out", "euros": 286}]},
          "mark": "bar",
          "encoding": {"y": {"field": "category", "type": "nominal", "sort": "-x", "title": null},
                       "x": {"field": "euros", "type": "quantitative", "title": "€"}}}}
```

Bad, and why:

- `"data": {"url": "https://example.com/d.csv"}`: nothing is fetched ([data-from-url](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/bad/data-from-url.json)).
- A pie of twelve slices, or twelve coloured lines: no one can tell them apart ([pie-of-twelve](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/bad/pie-of-twelve.json), [rainbow](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/bad/rainbow.json)).
- `"field": "amount"` when the rows have `euros` ([field-not-in-rows](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/bad/field-not-in-rows.json)).
- Two y axes on one chart: they read as one ([dual-axis](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/bad/dual-axis.json)).
- More rows: [too-many-rows](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/bad/too-many-rows.json), [no-data](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/bad/no-data.json), [no-mark](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/bad/no-mark.json).

## When it says no

A refused spec comes back as a failed call, one line per problem: where in the spec, what is wrong, what to do. For example:

    spec.encoding.y.field: "amount" isn't in the rows (they have category, euros)
    spec.encoding.color: 12 colours, more than 8 can be told apart; keep the largest and group the rest as Other, or use a bar chart

Fix each line where it points and call again. After two refusals, say the point in words instead.

## Checking it first (optional)

With `execute` (`skill` set to `vega-lite`), check a spec before sending it: the same rules as render_vega, then a compile with vl-convert to prove it draws. Write the spec with `write_file` first:

    python3 .skills/vega-lite/scripts/validate.py charts/spending.json

It prints `ok (compiled with vl-convert …)` or one problem per line. To look at it yourself, or to put it in a report or a deck, draw it and open it with `view_image`:

    python3 .skills/vega-lite/scripts/draw.py charts/spending.json charts/spending.png

Without `execute`, skip this: render_vega checks it anyway.

## Where this comes from

The rules are traceflow's: `scripts/vega_rules.py` is a copy, in Python, of `VegaLiteRules.java` in the traceflow repo (`backend/traceflow-parent/traceflow-effects/traceflow-tools/src/main/java/com/fifteen02/traceflow/tool/generative/`). The examples are the tool's, in [client-tools/render_vega/examples](https://github.com/fifteen02/traceflow-library/tree/main/client-tools/render_vega/examples) of the traceflow library. In the library, `python3 scripts/check_examples.py` runs every one of them; with `--source <traceflow checkout>` it also says when one differs from traceflow's own.
