# render_a2ui

A reply laid out by the agent: one A2UI 1.0 `createSurface` message whose components are a flat list joined by id from `root`, each a piece of [catalog.json](catalog.json) with literal values. The runtime checks the surface against the catalog before it is shown (at most 40 pieces, 5 levels, 4 buttons; each VegaChart's spec by `render_vega`'s rules); a surface that fails comes back as a failed call, one line per problem. A Button sends its `action.event.userMessage` as the person's next message.

## Reply

None: it only shows.

## In traceflow's apps

Each piece drawn by the chat app's own component: Text, Row, Column, Card, Divider, Button (primary in ink, the rest secondary), VegaChart (as `render_vega`), Places (as `show_places`), Schedule (as `show_schedule`), Table (as `show_table`), Sources (as `show_sources`).

## On a channel without UI

`channels` is `app`: only a client that says it draws it is offered the tool, never WhatsApp or another channel. A channel shown one all the same says the words of its Text pieces, a line each, in the order listed; buttons and other pieces are dropped.

## More

The a2ui skill teaches the pieces and layouts; its `scripts/validate.py` checks a surface with the same rules. [examples/](examples/) holds surfaces that pass (`good/`) and surfaces that fail with the line they get (`bad/`, `why` and `expect`).
