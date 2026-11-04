# confirm

The summary of what is about to happen, a yes and a no labelled `approve` and `decline` (Yes and No when left out), and room to say something else.

## Reply

`{"confirmed", "note"?}`: `confirmed` is true only on an explicit yes; anything else the person said goes in `note`.

## In traceflow's apps

A white panel: the summary as the lead line, `approve` as the primary button, `decline` beside it, and the composer for anything else.

## On a channel without UI

The summary as text and two buttons, Yes (`{"confirmed": true}`) and No (`{"confirmed": false}`); a channel's buttons say Yes and No whatever `approve` and `decline` are.

Buttons are drawn only when this is the one thing the turn asks; a turn that asks several things at once shows each and adds "This asks n things at once; answer them in the web app."
