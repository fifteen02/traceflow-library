# collect

The title and a form for the call's own `schema`, sent with a button labelled `submit` (the client's own when left out). A field the schema marks `"secret": true` is typed masked and never shown back.

## Reply

The filled object, fitting the call's `schema` (the reply schema is `{"type": "object", "x-schema-from": "schema"}`). A secret field holds its handle (`secret/<uuid>`), never the value.

## In traceflow's apps

The chat app has no card of its own for it: its Fallback card shows the tool's name as a caption and the arguments as labelled fields, answered in words when the reply is one string field, else skipped. The console's web app draws it as above.

## On a channel without UI

Not a form: its arguments as labelled fields (each argument's name made readable, values joined by commas), headed by the call's description, and "This needs a form; answer it in the web app." (a schema with no fields is answered by a typed line).

Buttons are drawn only when this is the one thing the turn asks; a turn that asks several things at once shows each and adds "This asks n things at once; answer them in the web app."
