# show_checks

Checks as they run: each its label, its status (pending, running, passed, failed) and what it found; a failed one how to fix it (markdown) and a link to act on it. Called again as the checks move on, it updates in place.

## Reply

None: it only shows.

## In traceflow's apps

The chat app has no card of its own for it: its Fallback card shows the tool's name as a caption and the arguments as labelled fields, answered in words when the reply is one string field, else skipped. The console's web app draws it as above.

## On a channel without UI

No drawing of its own: its arguments as labelled fields (each argument's name made readable, values joined by commas), headed by the call's description.
