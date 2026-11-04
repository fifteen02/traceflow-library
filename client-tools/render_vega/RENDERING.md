# render_vega

A chart from a Vega-Lite spec with its rows inline. The runtime checks the spec (at most 5000 rows, 8 colours, a pie of 6 slices, one y axis, every encoded field in the rows) and compiles it before it is shown; a spec that fails comes back as a failed call, one line per problem. A good one is drawn into the thread's workspace as `charts/<slug>.png` beside its spec `charts/<slug>.vl.json`, and the call gains a `picture` argument naming the PNG.

## Reply

None: it only shows.

## In traceflow's apps

Nothing for the call itself: the chart travels on the reply as its picture with the spec beside it, and the app draws the spec live from there.

## On a channel without UI

The picture, attached after the reply's text as an image (with the spec in its metadata, so a client that draws charts can draw it live). A picture that can't be sent (missing, over 15 MB) is said in a line instead: "(charts/x.png couldn't be sent: reason)".

## More

The rules are the vega-lite skill's `scripts/vega_rules.py`; [examples/](examples/) holds calls that pass (`good/`) and calls that fail with the line they get (`bad/`, `why` and `expect`).
