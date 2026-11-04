# open_url

The label as a button that opens `url` (https) in a new tab or window: a sign-in page, a bot to start. The page opened is the provider's.

## Reply

`{"opened"?}`: true unless the person said otherwise.

## In traceflow's apps

The chat app has no card of its own for it: its Fallback card shows the tool's name as a caption and the arguments as labelled fields, answered in words when the reply is one string field, else skipped. The console's web app draws it as above.

## On a channel without UI

Its arguments as labelled fields (each argument's name made readable, values joined by commas), headed by the call's description (the link among them), and "This needs a form; answer it in the web app."

Buttons are drawn only when this is the one thing the turn asks; a turn that asks several things at once shows each and adds "This asks n things at once; answer them in the web app."
