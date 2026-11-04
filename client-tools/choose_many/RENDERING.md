# choose_many

The question and each option as a choice to toggle, and a button that sends the picks; at least `min` and at most `max` when given.

## Reply

`{"choices"}`: the options picked, each as given, between `min` and `max`.

## In traceflow's apps

Choose many: a white panel with the question, linen rows with checkboxes (ink when ticked), "n picked" and a primary Send.

## On a channel without UI

The question, the options as a numbered list, and the note "Reply with the numbers of your picks, e.g. 1,3" with the bounds ("(1 to 3)"). A typed line of numbers (`1,3`) is read as those options; any other line isn't an answer to it.

Buttons are drawn only when this is the one thing the turn asks; a turn that asks several things at once shows each and adds "This asks n things at once; answer them in the web app."
