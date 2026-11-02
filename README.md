# traceflow skills

Skills for [traceflow](https://github.com/fifteen02/traceflow) agents: playbooks that tell an agent how to use traceflow's tools well. Each skill follows the [Agent Skills](https://agentskills.io) format, so any tool that reads `SKILL.md` folders can use it.

## Skills

| Skill | What it is for |
|---|---|
| [search-messages](skills/search-messages/SKILL.md) | Searching a person's own messages and emails: one person across chats, the latest version of a schedule, what is new, a chat by name, what to do when a search finds nothing. |

## A skill's folder

```
skills/<name>/
├── SKILL.md      the header (name, description, license, metadata) and the instructions
├── icon.svg      the skill's icon, named by metadata.icon in the header
└── …             any other files the instructions use (references, examples, scripts)
```

- `name` is the folder's name: lowercase letters, digits and hyphens.
- `metadata.icon` names the skill's icon, an SVG in the folder. traceflow shows it on the skill's card. No scripts, no links and no embedded images.
- `metadata.always: true` suggests the skill is read on every turn (its instructions in front of the agent, not only its name). It is where an install starts: an admin switches it on or off per installed skill.
- A skill made only of instructions needs nothing else.

### Icons

Every icon is one of a set, so a skill is known at a glance:

- a 64×64 tile, corner radius 18, a diagonal gradient (lighter top-left, darker bottom-right) and a thin white inner edge at 18% opacity;
- one white glyph for what the skill is about, with one translucent white shape behind it for depth;
- the tile's colour says the skill's area: teal for messages and people, blue for calendar and time, amber for files and documents, violet for the web, coral for money;
- it reads at 36px on a card, on light and dark pages alike.

## Installing in traceflow

An admin adds this repository as a skill source (Git, `github.com/fifteen02/traceflow-skills`), picks a skill and installs it, pinned to the commit it was installed from. An agent declares it by its folder:

```java
.tools(t -> t.skill(SkillDeclaration.from("github.com/fifteen02/traceflow-skills", "skills/search-messages")).all(TOOLS))
```

## Writing a skill

A skill is a folder with a `SKILL.md` in it. On every turn the agent sees each skill's `name` and `description`; when a task needs one, it calls `load_skill` and reads the body. The body can point to other files in the folder, and a skill with an environment can run its scripts.

Three examples follow, from the simplest up. All the names in them are made up.

### 1. Only instructions

```
skills/reply-drafts/
├── SKILL.md
└── icon.svg
```

```markdown
---
name: reply-drafts
description: How to draft a reply to one of the person's messages or emails in their own voice. Use it when they ask you to answer, reply to, write back to or get back to someone, or to say no politely. Not for writing new emails from scratch.
license: Apache-2.0
compatibility: traceflow agents that have the search_messages and search_messages_thread tools.
metadata:
  icon: icon.svg
  always: true
  author: your-github-handle
---

# Drafting replies

Never send anything. Write the draft, show it, and wait for the person to say it is right.

## Pick the recipe for the question

### A reply to one message ("reply to Ana")

1. Find the message with `search_messages` (`person` set to Ana) and read it in its thread with `search_messages_thread`.
2. Read two or three of the person's own earlier messages in that chat, to match how they write there: length, greeting, emoji or none.
3. Answer every question the message asks. Say what you could not answer and why.

### Saying no politely

1. Thank them, say no in the first two sentences, and give one reason at most.
2. Offer another time or another way when the person has given you one. Never make one up.
```

The header:

| Field | Rule |
|---|---|
| `name` | Required. 1–64 characters: lowercase letters, digits and single hyphens, not at the start or end. The same as the folder's name. |
| `description` | Required, at most 1024 characters. See below. |
| `license` | `Apache-2.0` for skills in this repository. |
| `compatibility` | Optional. What the skill needs: the tools it uses, the programs it runs. |
| `metadata.icon` | The icon's file in the folder (see [The icon](#4-the-icon)). Left out, traceflow looks for `icon.svg`. |
| `metadata.always` | Optional. `true` suggests the whole skill is read on every turn. Keep it for skills that most turns need; the admin decides in the end. |
| `metadata.author` | Optional. Your GitHub handle or your project's name. |

Write any other key under `metadata`. A top-level key the [Agent Skills](https://agentskills.io) format doesn't name is ignored, with a warning.

**The `description`** is all the agent knows about a skill until it loads it, so it decides whether the skill is ever used. Say what the skill is for and, above all, **when** to use it, in the words a person would use: "Use it when they ask you to answer, reply to, write back to…". Say when not to use it if another skill is close. Leave out how it works; that is the body's job. Avoid `: ` (a colon and a space) in a header value, or put the whole value in quotes.

**The body** is read only when the skill is loaded, so it can be longer, but it is still read in full each time. Write it for the agent:

- start with the rules that always hold ("Never send anything");
- then one short recipe per kind of question, each with a heading that quotes how a person asks it, and numbered steps naming the exact tools and arguments;
- say what to do when a step finds nothing or more than one answer;
- leave out what the agent knows already.

### 2. With files

Put what is long, or needed only some of the time, in its own file, and link to it from the body. The agent reads it with `read_file` when the link says to: the folder is at `.skills/<name>/` in the agent's workspace.

```
skills/trip-planning/
├── SKILL.md
├── icon.svg
└── reference.md      packing lists and checks per kind of trip
```

The body links to it with a path from the folder:

```markdown
## Packing and checks

Before you write a packing list, read [reference.md](reference.md) and take the section for the kind of trip (a weekend away, a work trip, a long trip abroad). Keep only what fits the weather and the plans the person told you about.
```

Every link in a `.md` file must lead to a file in the folder; traceflow warns at install when one doesn't.

### 3. With a script

A script does what is better done by code: a calculation, a file conversion, a call to a service. It runs in a **skill computer**, a container built from the skill's environment (an image and its Python packages), never in the agent's workspace.

```
skills/weather-forecast/
├── SKILL.md
├── icon.svg
├── requirements.txt  requests==2.32.3
└── scripts/
    └── forecast.py
```

```markdown
---
name: weather-forecast
description: The weather forecast for a place and the next few days, from the weather service the admin set up. Use it when the person asks about the weather, rain, temperature or what to wear, or before planning something outdoors.
license: Apache-2.0
compatibility: Python 3 with requests, and internet access to the weather service.
metadata:
  icon: icon.svg
  author: your-github-handle
  openclaw:
    requires:
      bins: [python3]
      env: [WEATHER_API_URL, WEATHER_API_KEY]
    primaryEnv: WEATHER_API_KEY
---

# Weather forecasts

Run the script with `execute`, with `skill` set to `weather-forecast`:

    python3 .skills/weather-forecast/scripts/forecast.py --place "Lisbon" --days 3

It prints one line per day as JSON: the date, the lowest and highest temperature in °C, and the chance of rain.

1. Ask which place when the person hasn't said and you don't know where they are.
2. Give the days they asked about, in a sentence each. Round temperatures to whole degrees.
3. If the script fails, say the forecast isn't available. Never guess the weather.
```

How the script is used:

- **Running it.** Commands start in the workspace's root, so the body names the script by its path from there: `.skills/<name>/scripts/…`. The `skill` argument of `execute` runs the command in the skill computer, beside the skill's files. Files the script writes for the person go in the workspace (`reports/forecast.json`), not in the skill's folder.
- **Its Python packages.** At install, traceflow reads the imports in the skill's scripts and lists any the environment lacks; the admin adds them to the environment, which is built once at install. Nothing is installed while the agent runs. Ship a `requirements.txt` with the versions you tested, so the admin can copy the lines. Use the standard library where you can.
- **Its programs.** List the programs the scripts run in `metadata.openclaw.requires.bins`, as [OpenClaw](https://github.com/openclaw/openclaw) skills do. The install check shows the ones the environment lacks.
- **Its settings.** List the environment variables the scripts read in `metadata.openclaw.requires.env` (and `primaryEnv`). Each becomes a setting the admin fills in, and the scripts read it from their environment. A setting whose name has a word like `KEY`, `TOKEN`, `SECRET` or `PASSWORD` is kept secret and masked. A setting's name can't be `PATH`, `HOME` or another the computer sets itself, or start with `LD_` or `PYTHON`.
- **Its network.** An environment has no network unless the admin gives it one. Say in `compatibility` when the skill needs the internet.

`scripts/forecast.py` reads its settings and prints, nothing more:

```python
import argparse
import json
import os

import requests


def main():
    parser = argparse.ArgumentParser(description="The forecast for a place.")
    parser.add_argument("--place", required=True)
    parser.add_argument("--days", type=int, default=3)
    args = parser.parse_args()

    answer = requests.get(
        os.environ["WEATHER_API_URL"],
        params={"q": args.place, "days": args.days},
        headers={"Authorization": "Bearer " + os.environ["WEATHER_API_KEY"]},
        timeout=20,
    )
    answer.raise_for_status()
    for day in answer.json()["days"]:
        print(json.dumps({"date": day["date"], "low": day["min_c"], "high": day["max_c"], "rain": day["rain_chance"]}))


if __name__ == "__main__":
    main()
```

### 4. The icon

Draw it in the style of the set (see [Icons](#icons)). The smallest icon that fits:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" role="img" aria-label="Reply drafts">
  <defs>
    <linearGradient id="tile" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#1FB58F"/>
      <stop offset="1" stop-color="#075E4A"/>
    </linearGradient>
  </defs>
  <rect width="64" height="64" rx="18" fill="url(#tile)"/>
  <rect x="0.75" y="0.75" width="62.5" height="62.5" rx="17.25" fill="none" stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="1.5"/>
  <circle cx="38" cy="26" r="14" fill="#FFFFFF" fill-opacity="0.28"/>
  <path d="M14 22a8 8 0 0 1 8-8h20a8 8 0 0 1 8 8v12a8 8 0 0 1-8 8H28l-8 7v-7.5A8 8 0 0 1 14 34z" fill="#FFFFFF"/>
</svg>
```

traceflow draws an icon as an image, so it runs nothing. It still refuses one that:

- holds a `<script>`, `<style>`, `<image>`, `<use>`, `<foreignObject>`, `<a>`, `<iframe>`, `<embed>`, `<object>` or `<feImage>` element (style with attributes, as above, not CSS);
- has an event handler (`onload`, `onclick`, …);
- links out of itself: an `href` or `url()` must point inside the file (`url(#tile)`), never to a file or a web address;
- has a `<!DOCTYPE>`, isn't well-formed XML with `<svg>` at its root, or is larger than 32 KB.

A refused icon is left off the card, with a warning at install; the skill still works.

### Trying it in traceflow

Before you open a pull request, install your skill in a traceflow of your own, from the **Skills** page:

- **From a git repository**: your fork's URL, your branch as the **Ref**, and the skill's folder (`skills/reply-drafts`).
- **Upload a zip**: a zip of the folder, or of what is in it, with `SKILL.md` at its root.

Installing shows the header as traceflow read it and any warnings: a missing link, a refused icon, an import or a program the environment lacks. Then give the skill to an agent and ask it the questions your recipes are for. Install it again after each change.

### Contributing

1. Fork this repository and make a branch.
2. Add your skill as one folder under `skills/`, named as its `name`, with its `SKILL.md`, its icon and its files. One skill per folder, and one skill per pull request.
3. Add a row for it to the [Skills](#skills) table.
4. Open a pull request saying what the skill is for and how you tried it.

Skills here are Apache-2.0, like the repository: by contributing, you license your skill under it. Use made-up names and data in examples (Ana, Lisbon, `api.example.com`), never a real person's details, and keep secrets out: a key belongs in a setting, never in a file.

## License

Apache-2.0. See [LICENSE](LICENSE).
