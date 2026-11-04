# ask_location

Why the agent asks, a button that shares the device's position once, for this answer, and one saying no.

## Reply

`{"shared"?, "latitude"?, "longitude"?, "accuracyMeters"?, "place"?}`: the coordinates when shared, the place typed or sent otherwise; `shared` false when the person said no.

## In traceflow's apps

A map card that shares the device's position once, and a No.

## On a channel without UI

The reason as text and the note "Share your location, or say where you are." A location pin (WhatsApp) comes back as the answer's `place` line; a typed place does too.

Buttons are drawn only when this is the one thing the turn asks; a turn that asks several things at once shows each and adds "This asks n things at once; answer them in the web app."
