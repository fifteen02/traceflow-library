# choose

The question and each option as a choice; exactly one is picked. With `primary`, the options are the step's actions, the primary first; `back` is drawn apart; `actions` are actions beside the choices, not choices; `submit` labels the button that sends the choice.

## Reply

`{"choice"}`: one of `options`, exactly as given.

## In traceflow's apps

Choose one: a white panel with the question as a title and the options as secondary pills; the pick turns ink.

## On a channel without UI

The question as text and a button per option, each answering `{"choice": option}`. A channel without buttons lists them under "Reply with one of:".

Buttons are drawn only when this is the one thing the turn asks; a turn that asks several things at once shows each and adds "This asks n things at once; answer them in the web app."
