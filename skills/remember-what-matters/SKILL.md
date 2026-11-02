---
name: remember-what-matters
description: When to save, check and forget what the person prefers (their diet, home city, units, how they like replies, who is who) with remember_preference, list_preferences and forget_preference. Read it when they say what they like or always want, correct something you knew about them, ask what you know about them, or ask you to forget something.
license: Apache-2.0
compatibility: traceflow agents that have the preference tools. Preferences are kept per conversation's session.
metadata:
  icon: icon.svg
  author: traceflow
  traceflow:
    tools: [remember_preference, list_preferences, forget_preference]
---

# Remembering what matters to the person

You have three tools:

- `remember_preference` saves one preference as a `key` (a few words: `diet`, `home city`, `reply length`) and a `value` (what they prefer, in their words). Saving under a key that is there already replaces it.
- `list_preferences` lists everything saved.
- `forget_preference` forgets one, by its `key` as it was saved.

## Always

- Save only what they said, or plainly confirmed, about themselves. Never save a guess, a mood or a one-off ("I'm tired today", "just this once").
- Ask before saving anything sensitive: health, money, religion, an address, someone else's details. "Shall I remember that you're allergic to nuts?"
- After saving, say it in one short line ("Noted: you're vegetarian."), not a paragraph.
- Before an answer a preference could change (a recipe, a time, units, a place), check `list_preferences` once in the conversation.

## Pick the recipe for what they said

### They say what they like or always want ("I'm vegetarian", "always answer in Spanish", "keep it short")

1. Pick a short, plain key for what it is about, and reuse a key that is saved already for the same thing (`list_preferences` when unsure). One thing per key: `diet` and `allergies` apart.
2. Save it with `remember_preference`, the value as they said it.
3. Use it from now on, starting with your next answer.

### They correct you ("I'm not vegetarian any more", "I moved to Porto")

1. Save the new value under the same key: it replaces the old one.
2. If the old one no longer applies at all and nothing replaces it, forget it instead (below).

### Something sounds lasting but they didn't say so ("I'll take the train", "we're in Lisbon this week")

Don't save it. If it would help next time, ask: "Do you always prefer the train? I can remember that."

### "What do you know about me?"

1. Call `list_preferences` and show what it lists, as it is. Say these are the preferences you keep, and that they can change or remove any of them.
2. If nothing is saved, say so.

### "Forget that" / "Forget my address" / "Forget everything"

1. Call `list_preferences` to find the key or keys they mean. When it isn't clear which, ask.
2. Say which ones you will forget and wait for their yes: forgetting can't be undone.
3. Forget each with `forget_preference`, then say what was forgotten.

## When it doesn't work

- **"Preferences are kept by a conversation's session; this turn has none":** nothing was kept. Say you can't remember things in this conversation, and use what they said for now.
- **"Not saved" or "Not forgotten" with a reason:** say why in a few words and fix the key or value if you can.
- **"Nothing was saved as …":** check the key with `list_preferences` and try the one listed.
- **A tool is missing:** say you can't remember preferences here, and keep to what they said in this conversation.
