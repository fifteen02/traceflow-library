---
name: a2ui
description: Lay a reply out in traceflow's chat app with render_a2ui, with a layout for each kind of answer - a recipe, instructions or steps, a day or month plan, places to go or eat, a booking, stays to compare, a budget or split, products, a route, a quiz, connecting a service, numbers and charts, an answer with its sources - each with the real photo of what it is about. Use it for every chat-app reply that is steps, a plan, options or numbers (not only when asked for a card); a single fact stays a sentence. Not for WhatsApp or other channels, where render_a2ui isn't offered.
license: Apache-2.0
compatibility: Only in traceflow's own chat app, where render_a2ui is offered (the skill isn't offered without it). Its scripts are optional, standard library only, and run in the skill computer of the documents environment (traceflow-skill-runtime, which has python3); vl-convert-python, to compile and draw a chart, comes from requirements.txt when that computer is built. Needs no internet.
metadata:
  icon: icon.svg
  author: traceflow
  traceflow:
    tools: [render_a2ui, execute, write_file, view_image]
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
- Values are literal. When several items share a shape, give the surface a `dataModel` and write the shape once (Many alike, below). Nothing writes the data: there are no inputs.
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
- `VegaChart`: A Vega-Lite chart, drawn live, its data inline. **spec** (object); height (number 120–600).
- `Places`: Places as cards, best first: one place, or several to pick from. title (string); **places** (list of {**name**, photo, rating, reviews, price, kind, distance, openNow, hours, address, mapsUrl, phone}, 1–8); from ({**latitude**, **longitude**}).
- `Schedule`: A day of the calendar as a timeline. **day** (string); summary (string); **items** (list of {**start**, end, **title**, place}, ≤30).
- `Table`: Rows of the same shape under their columns. title (string); **columns** (list of {**key**, **label**}, 1–8); **rows** (list of objects, ≤50).
- `Sources`: Where an answer comes from, in order. title (string); **sources** (list of {**title**, url, site, snippet}, 1–10).
<!-- /pieces -->

Every component may also carry `accessibility` and `metadata`. A Table's rows are objects keyed by its columns' `key`s, values as text ("€96"). A VegaChart's spec follows the chart rules: rows inline, at most 5000, 8 colours, a pie of 6 slices, one y axis (Charts, below, says which chart to pick).

## Layouts

**Steps, a plan, options or numbers are a layout; one fact is a sentence.** **And show the real thing whenever you can:** a place, a stay, a product, a dish or a person's venue has a photo somewhere (its own site, the listing, the maker's page, the recipe's page, its Google place); find it and put it in, an `Image` at the top of the card or as `Places` cards (their photos come from Google). A card about something real with no picture is the exception, when none can be found. A recipe, a set of instructions, a day, a choice between places, a budget: lay it out, without being asked to. Find the scenario below, read its file (`read_file` on `.skills/a2ui/layouts/<name>.json`), copy it and change its words and data. Each is a whole, valid surface. In the skeletons, `>` reads "has as children"; `data:` is the shape its dataModel takes.

### Scenarios

**Recipe** ([recipe](layouts/recipe.json)): a dish to cook. The dish's photo from the recipe's page when there is one (an `Image` first), serves and time, what you need, the steps numbered one to a line, one next step.

    root Column > summary Text (caption), needs Table, steps Column (one step Text per /steps), actions Row > shop Button (primary)
    data: {serves, minutes, ingredients: [{item, amount}], steps: [{n, text}]}

**Instructions** ([instructions](layouts/instructions.json)): setting something up. What you need first, the steps numbered, a button for done and one for stuck.

    root Column > needs Text (caption), steps Column (one step Text per /steps), actions Row > done Button (primary), stuck Button
    data: {steps: [{n, text}]}

**Reservation** ([reservation](layouts/reservation.json)): a booking to finish. The place (as `Places`, so its photo comes with it), what is already settled (the date and party, said once, never asked again), the open choice as a button each. Never say it's booked until the place confirms.

    root Column > place Places, settled Text (caption), times Row (one time Button per /times), sources Sources
    data: {dateLabel, people, times: [{at, variant}]}

**Day plan** ([day-plan](layouts/day-plan.json)): a day to read. The timeline and one line about it; no button when nothing needs doing.

    root Column > day Schedule, note Text (caption)

**Month plan** ([month-plan](layouts/month-plan.json)): a month at a glance. Its events by date, the one thing worth knowing, add and move.

    root Column > events Table (rows from /events), note Text (caption), actions Row > add Button, move Button
    data: {events: [{day, time, what}]}

**Stay** ([stay](layouts/stay.json)): one listing. Its photo from the listing (an `Image` first), what and where, its rating on its own provider's scale (9.2 / 10 stays 9.2 / 10), the price a night and in all, what it has, one step, then the listing as a source. Each fact once, and flat on the surface: a Card inside it only when there are several to tell apart.

    root Column > photo Image, heading Column > name, kind Text; rating, price, has Text; actions Row > book Button (primary); sources Sources

**Stay compare** ([stay-compare](layouts/stay-compare.json)): offers for the same dates, guests and currency. The dates once above them, a card each with the same facts in the same order, a button each.

    root Column > dates Text (caption), offers Row (one offer Card per /offers), actions Row > take-0 Button, take-1 Button
    data: {offers: [{site, name, rating, nightly, total}]}

**Stay budget** ([stay-budget](layouts/stay-budget.json)): an estimate, called one. The rate it rests on, each line, the total, buttons to change what it assumes. Work the numbers out before writing the surface; never invent a fee or a discount.

    root Column > basis Text (caption), lines Column (one line Row per /lines), total Text, change Row > three Buttons
    data: {rate, breakfast, total, lines: [{what, euros}]}

**Quiz** ([quiz](layouts/quiz.json)): one question at a time. Where you are, the question, its answers as buttons. Call the result a reflection, never an assessment.

    root Column > progress Text (caption), question Text, answers Column (one answer Button per /options)
    data: {options: [{label}]}

**Route** ([route](layouts/route.json)): stops in the order walked or driven, each opening in maps, how long it takes, one step.

    root Column > stops Places, length Text (caption), actions Row > start Button (primary)

**Products** ([products](layouts/products.json)): things to buy, from their makers' own pages. Each product's photo from its maker's page (an `Image` in its card), brand, name, what it is, the detail that matters, the pages as sources. No price or photo the maker's page doesn't have.

    root Column > items Column (one product Column per /products: brand, name, what Text, a Button), sources Sources
    data: {products: [{brand, name, what, detail}]}

**Connect** ([connect-calendar](layouts/connect-calendar.json), [connect-gmail](layouts/connect-gmail.json)): when a task needs a service that isn't connected. What it would let you do, what it can do, one Connect button. Never say it's connected until it is.

    root Column > title Text, benefit Text, can Column (one ability Text per /can), actions Row > connect Button (primary)
    data: {can: [{what}]}

**Connected apps** ([connected-apps](layouts/connected-apps.json)): the connections and where each stands, as the connections say, and the actions that change them.

    root Column > apps Table (rows from /apps), actions Row > connect Button, manage Button
    data: {apps: [{app, for, state}]}

**Morning brief** ([morning-brief](layouts/morning-brief.json)): what was missed. Today as a timeline, what came in that needs the person (only that), the first thing to do. Nothing to report is a line, without a surface.

    root Column > today Schedule, needs Table (rows from /needs), actions Row > first Button (primary)
    data: {needs: [{from, about, by}]}

**Inbox triage** ([inbox-triage](layouts/inbox-triage.json)): mail that needs the person, most pressing first. Who and what about, why it needs them (a date, a question asked), a reply each; the rest counted in a line, not listed.

    root Column > mails Column (one mail Column per /mails: what Text, why Text (caption), reply Button), rest Text (caption)
    data: {waiting, mails: [{from, subject, why, variant}]}

**Email draft** ([email-draft](layouts/email-draft.json)): a reply or an email to read before it goes. Who to and which thread, the words as they will be sent, send or change. The person is still asked before it sends; never say it went until the tool says so.

    root Column > to Text (caption), draft Card > draft-text Text, actions Row > send Button (primary), shorter Button, time Button

**Person** ([person](layouts/person.json)): someone as the messages know them. Their name, each way to reach them, when you last spoke and about what, the ways to reach out. Only addresses and numbers found; two people of one name are asked about, not merged.

    root Column > name Text, reach Table (rows from /reach), last Text (caption), actions Row > email Button (primary), message Button
    data: {lastOn, lastAbout, reach: [{how, at}]}

**Find a time** ([find-a-time](layouts/find-a-time.json)): when to meet. What was asked once (how long, which days), each slot both calendars show free as a button, the best primary.

    root Column > asked Text (caption), slots Column (one slot Button per /slots), note Text (caption)
    data: {week, slots: [{day, from, to, variant}]}

**Invite** ([invite](layouts/invite.json)): an invitation to answer. What, when and where once, whether the time is free, yes, maybe and no.

    root Column > what Text, when Text (caption), fits Text, actions Row > yes Button (primary), maybe Button, no Button

**Meeting brief** ([meeting-brief](layouts/meeting-brief.json)): before a meeting. When and with whom, what is still open between you one point a line, where each came from, one step.

    root Column > when Text (caption), points Column (one point Text per /points), sources Sources, actions Row > notes Button (primary)
    data: {points: [{n, text}]}

**To-dos** ([to-dos](layouts/to-dos.json)): the open list, soonest first. Each with when it is due and a done button, then one to add; done ones are gone, not crossed out.

    root Column > items Column (one item Row per /items: what Text (weight 1), done Button (borderless)), actions Row > add Button
    data: {items: [{what, due}]}

### More shapes

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

**Many alike** ([many-alike](layouts/many-alike.json)): rows of the same shape, written once over the surface's data, the amounts formatted for you.

    {"createSurface": {"surfaceId": "lisbon-split", "catalogId": "...",
      "dataModel": {"total": 1065, "people": 3, "costs": [{"what": "Apartment, 5 nights", "euros": 945}, ...]},
      "components": [
        {"id": "costs", "component": "Column", "children": {"path": "/costs", "componentId": "cost"}},
        {"id": "cost", "component": "Row", "justify": "spaceBetween", "children": ["cost-what", "cost-euros"]},
        {"id": "cost-what", "component": "Text", "text": {"@path": "what"}},
        {"id": "cost-euros", "component": "Text",
         "text": {"@call": "formatCurrency", "args": {"value": {"@path": "euros"}, "decimals": 0}}},
        {"id": "each", "component": "Text", "text": {"@call": "formatString", "args": {"value":
          "${formatCurrency(value: ${/total}, decimals: 0)} between ${/people} ${pluralize(value: ${/people}, one: 'person', other: 'people')}"}}},
        ...]}}

- `{"@path": "/costs/0/what"}` reads the data (a JSON Pointer); inside a template a path without `/` is the item's own (`what`).
- `children: {"path": "/costs", "componentId": "cost"}` draws `cost` (and what it holds) once per item.
- Functions: `formatString` (fills in `${/path}`, `${what}`, `${function(arg: value)}`), `formatCurrency` (€945), `formatNumber`, `formatDate` (`EEEE d MMMM`, `h:mm a`), `pluralize`, `join`. A Button's `userMessage` may be one too.
- The surface is checked as it will be drawn: the limits count the copies, and a path that isn't in the data is refused.

    root Column > answer Text, sources Sources

Worked examples, each with the question asked and the line said before it, are in the tool's [examples/good](https://github.com/fifteen02/traceflow-library/tree/main/client-tools/render_a2ui/examples/good).

## Charts

A chart is a `VegaChart` piece: a [Vega-Lite](https://vega.github.io/vega-lite/) spec with its rows inline, drawn live, on its own or beside a table and a next step ([chart-table-next](layouts/chart-table-next.json)).

- **A chart only when it helps.** Two or three numbers are a sentence ("€412 on groceries, €286 eating out"). A chart is for a shape: a trend, a ranking, a share, a spread, more numbers than a sentence holds. Say the point in one line; never read its numbers back in words.
- **The rows go inline** in `data.values`, already summed or averaged to what the chart shows. Never a `url`: nothing is fetched.
- **Titles in words.** An axis says what and in what unit ("Steps a day", "€"); set a title to `null` when the labels say it already.
- **One colour for one series.** Colour only to tell series apart, never to decorate.
- **Made-up numbers never.** Chart only what you read or worked out, and say where it came from.

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

A pie (`"mark": "arc"`) only for parts of one whole, 6 slices at most; bars read better almost always. The limits: at most **5000 rows**, **8 colours**, a pie of **6 slices**, **one y axis** (no `"resolve": {"scale": {"y": "independent"}}`), every field an encoding names in the rows or made by a `transform` (`as`), and a `mark` wherever there is an `encoding`.

    {"id": "chart", "component": "VegaChart",
     "spec": {"data": {"values": [{"category": "Groceries", "euros": 412}, {"category": "Eating out", "euros": 286}]},
              "mark": "bar",
              "encoding": {"y": {"field": "category", "type": "nominal", "sort": "-x", "title": null},
                           "x": {"field": "euros", "type": "quantitative", "title": "€"}}}}

Bad: rows from an address ([data-from-url](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/bad/data-from-url.json)); a pie of twelve slices or twelve coloured lines ([pie-of-twelve](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/bad/pie-of-twelve.json), [rainbow](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/bad/rainbow.json)); a field the rows don't have ([field-not-in-rows](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/bad/field-not-in-rows.json)); two y axes ([dual-axis](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_vega/examples/bad/dual-axis.json)).

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
- [binding-not-in-data](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/binding-not-in-data.json): a `@path` the dataModel doesn't have.
- [unknown-function](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/unknown-function.json): a `@call` that isn't one of the functions.
- [template-not-a-list](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/template-not-a-list.json): a template over something that isn't a list.
- [text-variant-heading](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/text-variant-heading.json): `"variant": "h1"`; use bold.
- [button-without-message](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/button-without-message.json): a Button with no `userMessage`.
- [too-many-buttons](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/too-many-buttons.json): five buttons, a menu not a reply.
- [chart-from-url](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/chart-from-url.json): a chart's rows from an address.
- [image-not-https](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/image-not-https.json): a photo that isn't at an https address on the web (a file, a `data:` picture).
- [unknown-piece](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/unknown-piece.json), [wrong-version](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/wrong-version.json), [two-messages](https://github.com/fifteen02/traceflow-library/blob/main/client-tools/render_a2ui/examples/bad/two-messages.json): a piece, a version or a message shape the app doesn't have.

## Checking it first (optional)

With `execute` (`skill` set to `a2ui`), write the arguments with `write_file` and check them with the same rules as render_a2ui:

    python3 .skills/a2ui/scripts/validate.py surfaces/dinner.json

It prints `ok` or one problem per line. To check one chart's spec on its own and compile it with vl-convert, proving it draws, write the spec to a file and run `validate_chart.py`; to look at it, draw it and open it with `view_image`:

    python3 .skills/a2ui/scripts/validate_chart.py charts/spending.json
    python3 .skills/a2ui/scripts/draw_chart.py charts/spending.json charts/spending.png

Without `execute`, skip this: render_a2ui checks it anyway.

## Where this comes from

The tool, its catalog and its examples live in [client-tools/render_a2ui](https://github.com/fifteen02/traceflow-library/tree/main/client-tools/render_a2ui) of the traceflow library. `catalog.json` here is a copy of the tool's, kept so the validator works where only this skill is installed; `scripts/validate.py` is a copy, in Python, of `A2uiSurfaces.java` and `A2uiCatalog.java` (and `scripts/data.py` of `A2uiData.java`) in the traceflow repo (`backend/traceflow-parent/traceflow-effects/traceflow-tools/src/main/java/com/fifteen02/traceflow/tool/generative/`), and `scripts/vega_rules.py` of `VegaLiteRules.java`. The chart examples are render_vega's, in [client-tools/render_vega/examples](https://github.com/fifteen02/traceflow-library/tree/main/client-tools/render_vega/examples), which `scripts/validate_chart.py` runs in the library's check. In the library, `python3 scripts/check_examples.py` runs the tool's examples and this skill's layouts, checks the pieces list above against `catalog.json` (`scripts/pieces.py` makes it), and says when `catalog.json` differs from the tool's; with `--source <traceflow checkout>` it also says when the tool's catalog or examples differ from traceflow's.
