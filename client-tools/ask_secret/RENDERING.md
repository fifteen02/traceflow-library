# ask_secret

The label, the help (markdown) and a masked field. The client never puts the value in its reply: it posts it to the console's secret endpoint (`POST /api/wizards/threads/{sessionId}/secrets` with the value) and replies with the handle it gets back.

## Reply

`{"handle"}`: the handle the secret endpoint gave. A reply holding anything but a handle is refused.

## In traceflow's apps

The chat app has no card of its own for it: its Fallback card shows the tool's name as a caption and the arguments as labelled fields, answered in words when the reply is one string field, else skipped. The console's web app draws it as above.

## On a channel without UI

Its arguments as labelled fields (each argument's name made readable, values joined by commas), headed by the call's description, and "Reply in text." A typed value isn't a handle and is refused: a secret is given in the web app or the console.

Buttons are drawn only when this is the one thing the turn asks; a turn that asks several things at once shows each and adds "This asks n things at once; answer them in the web app."
