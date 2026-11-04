# upload

The label, a file picker taking the `accept`ed types up to `maxBytes` (0 for no limit), and a field for where the file comes from when `attributionRequired`.

## Reply

`{"file": {"filename", "mimeType", "content"}, "attribution"?}`: the file base64, and where it comes from.

## In traceflow's apps

The chat app has no card of its own for it: its Fallback card shows the tool's name as a caption and the arguments as labelled fields, answered in words when the reply is one string field, else skipped. The console's web app draws it as above.

## On a channel without UI

Its arguments as labelled fields (each argument's name made readable, values joined by commas), headed by the call's description, and "This needs a form; answer it in the web app."

Buttons are drawn only when this is the one thing the turn asks; a turn that asks several things at once shows each and adds "This asks n things at once; answer them in the web app."
