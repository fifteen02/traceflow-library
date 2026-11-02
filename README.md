<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
    <img src="assets/logo-light.svg" height="64" alt="traceflow">
  </picture>
</p>

<h1 align="center">traceflow skills</h1>

Skills for [traceflow](https://github.com/fifteen02/traceflow) agents: playbooks that tell an agent how to use traceflow's tools well. Each skill is a folder: a `SKILL.md` with a short header and the instructions, and any files, scripts and icon it uses.

## Skills

| Skill | What it is for |
|---|---|
| [search-messages](skills/search-messages/SKILL.md) | Searching a person's own messages and emails: one person across chats, the latest version of a schedule, what is new, a chat by name, what to do when a search finds nothing. |
| [remember-what-matters](skills/remember-what-matters/SKILL.md) | When to save, check and forget what the person prefers, and when not to: guesses, one-offs, anything sensitive without asking. |
| [daily-brief](skills/daily-brief/SKILL.md) | The person's day in a dozen lines, most pressing first: today's calendar, what is new in their messages, and what waits for their reply. |
| [calendar-assistant](skills/calendar-assistant/SKILL.md) | Finding a free time, checking for clashes, and saying exactly what will change before adding, moving or cancelling an event. |
| [read-documents](skills/read-documents/SKILL.md) | Any PDF, Word, Excel or PowerPoint file as text, tables included, scanned pages read by OCR. Scripts on the skill computer as it comes. |
| [skill-review](skills/skill-review/SKILL.md) | Checking a community skill before an admin installs it: what it runs, where it reaches, the secrets it asks for, what it installs, and what doesn't match its description. |

## A skill's folder

```
skills/<name>/
├── SKILL.md          the header (name, description, license, metadata) and the instructions
├── icon.svg          the skill's icon, named by metadata.icon in the header
├── requirements.txt  the Python packages its scripts import, when it has scripts
└── …                 any other files the instructions use (references, examples, scripts)
```

- `name` is the folder's name: lowercase letters, digits and hyphens.
- `metadata.icon` names the skill's icon, an SVG in the folder. traceflow shows it on the skill's card. No scripts, no links and no embedded images.
- `metadata.traceflow.tools` names the tools its instructions use; `metadata.traceflow.requires.bins` the programs its scripts need beyond the skill computer's.
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

[docs/writing-a-skill.md](docs/writing-a-skill.md) is a step-by-step guide: the tools an agent can have, what the skill computer already has, the header, and a worked example of each kind of skill.

| Kind | Example | It declares |
|---|---|---|
| Text only | `reply-drafts` | The tools its instructions use |
| With Python packages | `qr-codes` | Its tools, and its packages in `requirements.txt` |
| With programs | `photo-details` | Its tools, and its programs in `requires.bins` |
| With both | `diagrams` | All three |

traceflow never guesses what a skill needs: it installs only what the skill declares, and says at install what the skill uses but doesn't declare.

## Contributing

Fork this repository, add your skill as one folder under `skills/`, add a row to the [Skills](#skills) table, and open a pull request saying what the skill is for and how you tried it. One skill per pull request. Skills here are Apache-2.0; use made-up names and data in examples, and keep secrets out of files. The [guide](docs/writing-a-skill.md#7-trying-it-then-contributing-it) says how to try a skill in your own traceflow first.

## License

Apache-2.0. See [LICENSE](LICENSE). The robot in the logo is drawn from [agent-robot-avatar](https://www.npmjs.com/package/agent-robot-avatar), MIT; see [its licence](assets/LICENSE-agent-robot-avatar).
