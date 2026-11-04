---
name: a2ui
description: How to lay a reply out in traceflow's chat app with render_a2ui - cards to pick from, a day with a clash, a chart with a table and a next step, options side by side, an answer with its sources, and buttons that send the person's next message. Use it when a reply in the chat app would be easier to act on or compare as a layout than as text. Not for WhatsApp or other channels, where render_a2ui isn't offered.
license: Apache-2.0
compatibility: Only in traceflow's own chat app, where render_a2ui is offered (the skill isn't offered without it). Its scripts are optional, standard library only, and run in the skill computer of the documents environment (traceflow-skill-runtime, which has python3). Needs no internet.
metadata:
  icon: icon.svg
  author: traceflow
  traceflow:
    tools: [render_a2ui, execute, write_file]
    requires:
      tools: [traceflow/render_a2ui@1]
---

# Laying a reply out with render_a2ui

[A2UI](https://github.com/a2ui-project/a2ui) is a protocol for an agent to describe a piece of UI as data: a flat list of components, joined by id, that the app draws with its own pieces. traceflow's chat app draws A2UI 1.0 surfaces from one catalog, `catalog.json` beside this file. The tool itself, `traceflow/render_a2ui@1`, is defined in the library's [client-tools/render_a2ui](https://github.com/fifteen02/traceflow-library/tree/main/client-tools/render_a2ui).

## The message

`render_a2ui` takes `{"messages": [one message]}`:

```json
{"messages": [{"version": "1.0", "createSurface": {
  "surfaceId": "passport",
  "catalogId": "github.com/fifteen02/traceflow:chat/v1",
  "components": [
    {"id": "root", "component": "Column", "children": ["answer", "remind"]},
    {"id": "answer", "component": "Text", "text": "Your passport expires on **12 March**."},
    {"id": "remind", "component": "Button", "child": "remind-label", "variant": "primary",
     "action": {"event": {"name": "reply", "userMessage": "Remind me to renew my passport on 1 February"}}},
    {"id": "remind-label", "component": "Text", "text": "Remind me in February"}
  ]}}]}
```

- One `createSurface`, its components in it; no `updateComponents`, `updateDataModel` or `deleteSurface`.
- A flat list: each component has an `id` and names its `component`; a parent lists its children by id (`child`, `children`). One has the id `root`.
- Values are literal: no `@path`, `@call`, `@index`, templates or data model. Write the value itself.
- A Button sends its `action.event.userMessage` as the person's next message, exactly as if they typed it.

## The pieces

What the chat app can draw: each piece, what it is for, and its properties (required ones in **bold**).

<!-- pieces: made by scripts/pieces.py -->
- `Text`: Words: a line of the reply (body) or a quiet note (caption). Simple Markdown (bold, italics) only. **text** (string ≤600); variant (caption | body); weight (a number, its share of a Row).
- `Row`: Children side by side, wrapping when there is no room: a row of buttons. **children** (ids, 1–12); justify (center | end | spaceAround | spaceBetween | spaceEvenly | start | stretch); align (start | center | end | stretch); weight (a number, its share of a Row).
- `Column`: Children one under another: most surfaces' root. **children** (ids, 1–12); justify (start | center | end | spaceBetween | spaceAround | spaceEvenly | stretch); align (start | center | end | stretch); weight (a number, its share of a Row).
- `Card`: A panel around one child (a Column for several). **child** (an id); weight (a number, its share of a Row).
- `Divider`: A line between parts. axis (horizontal | vertical).
- `Image`: A real photo from the web of what the reply is about (from a place's own site, a product's page), at its https address: the app fetches it and credits its site. Never a made-up picture standing in for a real place or thing. **url** (string ≤2000); **alt** (string ≤200); caption (string ≤200); weight (a number, its share of a Row).
- `Button`: Sends action.event.userMessage as the person's next message when pressed. Its child is a Text: its label. primary for the one thing you recommend, default for the rest. **child** (an id); variant (default | primary | borderless); **action** ({event: {**name**, **userMessage** ≤300}}); weight (a number, its share of a Row).
- `VegaChart`: A Vega-Lite chart, drawn live: the spec as render_vega takes it, its data inline. **spec** (object); height (number 120–600).
- `Places`: Places to pick from as cards, best first, as show_places draws them. title (string); **places** (list of {**name**, photo, rating, reviews, price, kind, distance, openNow, hours, address, mapsUrl, phone}, 1–8); from ({**latitude**, **longitude**}).
- `Schedule`: A day of the calendar as a timeline, as show_schedule draws it. **day** (string); summary (string); **items** (list of {**start**, end, **title**, place}, ≤30).
- `Table`: Rows of the same shape under their columns. title (string); **columns** (list of {**key**, **label**}, 1–8); **rows** (list of objects, ≤50).
- `Sources`: Where an answer comes from, in order. title (string); **sources** (list of {**title**, url, site, snippet}, 1–10).
<!-- /pieces -->

Every component may also carry `accessibility` and `metadata`. A Table's rows are objects keyed by its columns' `key`s, values as text ("€96"). A VegaChart's spec follows the chart rules of render_vega: rows inline, at most 5000, 8 colours, a pie of 6 slices, one y axis (the vega-lite skill says how to pick a chart).

## Layouts

Seven shapes cover most replies. Each is a whole, valid surface in `layouts/`; copy the one that fits and change its words. In the skeletons, `>` reads "has as children".

**Answer and actions** ([answer-and-actions](layouts/answer-and-actions.json)): an answer in a line or two, then what to do next.

    root Column > answer Text, actions Row
    actions Row > remind Button (primary), how Button      each Button > its label Text

**List and pick** ([list-and-pick](layouts/list-and-pick.json)): things to choose from, best first, your pick as the primary button.

    root Column > places Places, note Text (caption), actions Row > go Button (primary), more Button

**Day and clash** ([day-and-clash](layouts/day-and-clash.json)): the day, the clash in words, the way out.

    root Column > schedule Schedule, clash Text, actions Row > move Button (primary), keep Button

**Chart, table, next step** ([chart-table-next](layouts/chart-table-next.json)): the shape, the detail, one step.

    root Column > chart VegaChart, table Table, actions Row > budget Button (primary)

**Side by side** ([side-by-side](layouts/side-by-side.json)): two or three options, a card each, each its own button.

    root Row > a Card (weight 1), b Card (weight 1)
    a Card > a-body Column > a-what Text ("**Lisbon** · €212"), a-pick Button

**Real photo** ([real-photo](layouts/real-photo.json)): a real place or thing as itself, its own photo from the web, then the next step.

    root Column > photo Image, note Text (caption), book Button (primary)

**Answer with sources** ([answer-with-sources](layouts/answer-with-sources.json)): the answer, then where it comes from; no buttons when there is nothing to do.

    root Column > answer Text, sources Sources

Worked examples, each with the question asked and the line said before it, are in the tool's [examples/good](https://github.com/fifteen02/traceflow-library/tree/main/client-tools/render_a2ui/examples/good).

## Rules

- **Say the point in your words first**, in the reply's text; the surface carries what words can't. Never only a surface.
- **A surface only when it helps the person act or compare.** A plain answer stays text.
- **A real place, person or thing is shown as itself, never made up.** Its photo is an `Image` at the https address where you found it (the place's own site, a product's page; the app fetches it and credits the site), or `Places` cards, whose photos the app fetches from Google. Never `make_picture` for something real, and never present a made-up picture as it; with no real photo, say so and give the link.
- **One primary button at most**, for the one thing you recommend; the rest `default`.
- **Button labels short** (a few words, "Move the bank to 14:00"); the `userMessage` is what the person would say, whole and on its own ("Move the call with the bank to 14:00 on Friday"), since it arrives as their next message.
- **At most 4 buttons, 40 pieces and 5 levels** (root is the first). Show less rather than more.
- **Text is `body` or `caption`.** There are no heading variants: write a heading as `**bold**`.
- A Button's `child` is a Text, its label. Every id is used once and every piece but root is some piece's child.
- `surfaceId`: a short name of letters, digits, `-` and `_` ("dinner-tonight").

## When it says no

A refused surface comes back as a failed call, one line per problem, each saying where (`createSurface.components[3] (book)` is the fourth component, id `book`) and what to do:

    createSurface.components[0] (root).variant: "h1" isn't one of [caption, body]
    components (actions): child "book" isn't a component of the surface
    components: 5 buttons, more than 4; offer the few that matter

Fix each line where it points and send the whole surface again. After two refusals, give the reply as text.

Bad, and why (each in the tool's [examples/bad](https://github.com/fifteen02/traceflow-library/tree/main/client-tools/render_a2ui/examples/bad), with the problem it gets):

- [no-root](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/no-root.json): no piece has the id `root`.
- [missing-child](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/missing-child.json): a child id that isn't a component.
- [orphan](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/orphan.json): a piece no one has as a child is never drawn.
- [cycle](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/cycle.json): a piece inside itself.
- [data-binding](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/data-binding.json): `{"@path": "/user/name"}` where a value goes.
- [text-variant-heading](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/text-variant-heading.json): `"variant": "h1"`; use bold.
- [button-without-message](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/button-without-message.json): a Button with no `userMessage`.
- [too-many-buttons](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/too-many-buttons.json): five buttons, a menu not a reply.
- [chart-from-url](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/chart-from-url.json): a chart's rows from an address.
- [image-not-https](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/image-not-https.json): a photo that isn't at an https address on the web (a file, a `data:` picture).
- [unknown-piece](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/unknown-piece.json), [wrong-version](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/wrong-version.json), [two-messages](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/two-messages.json): a piece, a version or a message shape the app doesn't have.

## Checking it first (optional)

With `execute` (`skill` set to `a2ui`), write the arguments with `write_file` and check them with the same rules as render_a2ui:

    python3 .skills/a2ui/scripts/validate.py surfaces/dinner.json

It prints `ok` or one problem per line. It doesn't compile charts; the vega-lite skill's `validate.py` does. Without `execute`, skip this: render_a2ui checks it anyway.

## Where this comes from

The tool, its catalog and its examples live in [client-tools/render_a2ui](https://github.com/fifteen02/traceflow-library/tree/main/client-tools/render_a2ui) of the traceflow library. `catalog.json` here is a copy of the tool's, kept so the validator works where only this skill is installed; `scripts/validate.py` is a copy, in Python, of `A2uiSurfaces.java` and `A2uiCatalog.java` in the traceflow repo (`backend/traceflow-parent/traceflow-effects/traceflow-tools/src/main/java/com/fifteen02/traceflow/tool/generative/`), and `scripts/vega_rules.py` of `VegaLiteRules.java`, the same file as the vega-lite skill's. In the library, `python3 scripts/check_examples.py` runs the tool's examples and this skill's layouts, checks the pieces list above against `catalog.json` (`scripts/pieces.py` makes it), and says when `catalog.json` differs from the tool's; with `--source <traceflow checkout>` it also says when the tool's catalog or examples differ from traceflow's.
