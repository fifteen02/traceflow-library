# ask

The question, and each suggestion as an answer to pick. The person may also answer in their own words.

## Reply

`{"answer"}`: a suggestion as given, or the person's own words.

## In traceflow's apps

Question: a white panel with the question as a title and "Reply in your own words" as a caption; suggestions as secondary pills; the answer is typed in the composer.

## On a channel without UI

The question as text, a button per suggestion (each answering `{"answer": suggestion}`), and the note "Reply in your own words, or pick one." ("Reply in your own words." without suggestions). A typed line is the answer.

Buttons are drawn only when this is the one thing the turn asks; a turn that asks several things at once shows each and adds "This asks n things at once; answer them in the web app."
