<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
    <img src="assets/logo-light.svg" height="64" alt="traceflow">
  </picture>
</p>

<h1 align="center">traceflow library</h1>

Skills and client tools for [traceflow](https://github.com/fifteen02/traceflow) agents and clients.

- A **skill** is a playbook that tells an agent how to use traceflow's tools well: a folder with a `SKILL.md` (a short header and the instructions) and any files, scripts and icon it uses.
- A **client tool** is a tool the agent calls and the person's client draws: a question, a choice, a plan, a chart, a laid-out reply. A folder with its definition (`tool.json`), what a client must draw for it (`RENDERING.md`) and example calls.

traceflow installs `traceflow`'s client tools from this repository, pinned to a commit, and installs a skill from it when an admin picks one.

## Skills

| Skill | What it is for |
|---|---|
| [search-messages](skills/search-messages/SKILL.md) | Searching a person's own messages and emails: one person across chats, the latest version of a schedule, what is new, a chat by name, what to do when a search finds nothing. |
| [remember-what-matters](skills/remember-what-matters/SKILL.md) | When to save, check and forget what the person prefers, and when not to: guesses, one-offs, anything sensitive without asking. |
| [daily-brief](skills/daily-brief/SKILL.md) | The person's day in a dozen lines, most pressing first: today's calendar, what is new in their messages, and what waits for their reply. |
| [calendar-assistant](skills/calendar-assistant/SKILL.md) | Finding a free time, checking for clashes, and saying exactly what will change before adding, moving or cancelling an event. |
| [read-documents](skills/read-documents/SKILL.md) | Any PDF, Word, Excel or PowerPoint file as text, tables included, scanned pages read by OCR. Scripts on the skill computer as it comes. |
| [skill-review](skills/skill-review/SKILL.md) | Checking a community skill before an admin installs it: what it runs, where it reaches, the secrets it asks for, what it installs, and what doesn't match its description. |
| [a2ui](skills/a2ui/SKILL.md) | Laying a reply out in traceflow's chat app with [`render_a2ui`](client-tools/render_a2ui/): its A2UI 1.0 pieces, seven layouts, charts (which chart for which question, a spec that passes first time), buttons that send the person's next message, and how to read a refusal. Requires `traceflow/render_a2ui@1`. |

## Client tools

| Tool | What it does | Channels |
|---|---|---|
| [ask](client-tools/ask/) | A question answered in words, or by picking a suggestion. | all |
| [choose](client-tools/choose/) | Pick exactly one of the options. | all |
| [choose_many](client-tools/choose_many/) | Pick several of the options, between bounds. | all |
| [confirm](client-tools/confirm/) | Approve something before it happens. | all |
| [collect](client-tools/collect/) | Fill in a form; the reply fits the call's own schema. | all |
| [upload](client-tools/upload/) | A file, of the accepted types and size. | all |
| [ask_location](client-tools/ask_location/) | Where the person is, shared once or said, when an answer depends on it. | all |
| [show_plan](client-tools/show_plan/) | A plan's steps, each with its status. | all |
| [update_plan](client-tools/update_plan/) | The plan the agent is working through, pinned above the chat. | all |
| [show_progress](client-tools/show_progress/) | How far along something is, as a bar. | all |
| [show_status](client-tools/show_status/) | A status line of segments, each with its tone. | all |
| [react](client-tools/react/) | One emoji on the person's message. | all |
| [show_object](client-tools/show_object/) | A value under its label, laid out by its schema. | all |
| [show_sources](client-tools/show_sources/) | Sources as citation cards. | all |
| [show_table](client-tools/show_table/) | Rows of the same shape as a table. | all |
| [show_places](client-tools/show_places/) | Places to compare and pick from, best first. | all |
| [show_schedule](client-tools/show_schedule/) | A day of the calendar as a timeline. | all |
| [render_vega](client-tools/render_vega/) | A chart from a Vega-Lite spec, checked and drawn; a picture on a channel. | all |
| [open_url](client-tools/open_url/) | A link to open: a sign-in page, a bot to start. | all |
| [ask_secret](client-tools/ask_secret/) | A secret, such as a bot token, kept as a handle. | all |
| [show_code](client-tools/show_code/) | A code to enter on another device or site. | all |
| [show_command](client-tools/show_command/) | A command to run elsewhere. | all |
| [show_checks](client-tools/show_checks/) | Checks as they run, a failed one with its fix. | all |
| [show_file](client-tools/show_file/) | A file of the thread's workspace; the file itself on a channel. | all |
| [show_pairing](client-tools/show_pairing/) | A QR or a code that links a device. | all |
| [render_a2ui](client-tools/render_a2ui/) | A reply laid out as an A2UI 1.0 surface of the chat app's pieces. | app |

`all`: every client draws it, a channel as text or media. `app`: only a client that says it draws it (traceflow's chat app); a harness may declare it only where its config says the client does.

## A client tool's folder

```
client-tools/<name>/
├── tool.json         the definition: id, name, version, description, parameters, reply, rendersOnly, channels, icon
├── RENDERING.md      what a client draws, what the reply is, what a channel without UI falls back to
├── icon.svg          its icon, as tool.json's icon names (see Icons)
├── examples/
│   ├── good/         calls that pass: the arguments, with notes (asked, said, why) beside them
│   └── bad/          calls that are refused, each with why and the line it gets (expect)
└── …                 any file the tool needs (render_a2ui's catalog.json)
```

```json
{
  "id": "traceflow/render_vega@1",
  "name": "render_vega",
  "version": 1,
  "description": "What the model reads.",
  "parameters": { "type": "object", "properties": { "…": {} }, "required": ["spec"] },
  "rendersOnly": true,
  "channels": "all"
}
```

- `name` is the folder's name and what the model calls; `parameters` is the JSON Schema of the arguments, with traceflow's extension keys (`x-pick-from`, `x-schema-from`, …) kept.
- `reply` is the JSON Schema of the person's answer. A tool that only shows (`rendersOnly: true`) has none.

## Ids and namespaces

- A client tool's id is `namespace/name@major`: `traceflow/ask@1`.
- A namespace is a source an admin trusts. `traceflow` is this library, seeded in every console, and **reserved**: no one authors a `traceflow/…` tool. A person's own tools are under their account (`mark/…`); a team publishes under its own source (`acme/…`), from its own repository laid out like this one.
- **Versioning:** a breaking change to the parameters or the reply bumps the major (`@2`), in the same folder. A change that breaks nothing (a clearer description, an optional parameter) keeps it. Apps keep a renderer per major, so old threads draw as they did.
- **Skills reference tools by id** in `requires.tools`, so a skill is offered only where that definition, at that major, is.

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
- `metadata.traceflow.requires.tools` names the tools the skill can't do without: a skill isn't offered to an agent that lacks one of them. A client tool is named by its id (`traceflow/render_a2ui@1`, see [Ids and namespaces](#ids-and-namespaces)), so only that definition at that major matches; a bare name matches by name only. Its other tools, listed in `tools` only, are ones it can manage without (a skill whose scripts are optional still helps an agent with no `execute`).
- A skill **references** a client tool, never copies it: its instructions link to the tool's folder here. A file its scripts need at run time stays in the skill, since a skill is installed on its own (the a2ui skill keeps a copy of the tool's `catalog.json`, which `scripts/check_library.py` holds identical).
- `metadata.always: true` suggests the skill is read on every turn (its instructions in front of the agent, not only its name). It is where an install starts: an admin switches it on or off per installed skill.
- A skill made only of instructions needs nothing else.

### Icons

Every skill and client tool has an icon (`icon.svg` in its folder), and every icon is one of a set, so they read as one family:

- traceflow's own tile: the squircle of its logo (`M32 0C58 0 64 6 64 32S58 64 32 64 0 58 0 32 6 0 32 0Z`) in ink `#17161A`, the same for every icon;
- on it one glyph naming what the skill or tool is about, from [Ant Design's icons](https://github.com/ant-design/ant-design-icons) in their outlined style, 32 units square at the tile's centre (x 16, y 16), moved there by a `transform` on the glyph's own paths;
- the glyph filled with one diagonal gradient (`linearGradient` x1 0, y1 0, x2 1, y2 1): `#F2C94C` at 0, `#6FB1E8` at .5, `#B08CF0` at 1, its id the icon's own (`tf-icon-<name>`) so icons on one page never share one;
- nothing else: no colour per area (the glyph tells them apart), no script, style, image, link or `use` (traceflow refuses those; `scripts/check_library.py` checks every client tool's);
- it reads at 36px on a card, on light and dark pages alike.

The glyphs are Ant Design's (`@ant-design/icons-svg`), © Alibaba, under the [MIT licence](https://github.com/ant-design/ant-design-icons/blob/master/LICENSE).

## Installing in traceflow

The console installs `traceflow`'s client tools from this repository at the commit it pins, and offers a newer commit as an update. An admin adds this repository as a skill source (Git, `github.com/fifteen02/traceflow-library`), picks a skill and installs it, pinned to the commit it was installed from. An agent declares it by its folder:

```java
.tools(t -> t.skill(SkillDeclaration.from("github.com/fifteen02/traceflow-library", "skills/search-messages")).all(TOOLS))
```

## Writing a client tool

[docs/writing-a-client-tool.md](docs/writing-a-client-tool.md) is a step-by-step guide: the definition, what a client must draw, the channel fallback, examples, and versioning.

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

Fork this repository, add your skill as one folder under `skills/` (or a client tool under `client-tools/`), add a row to the [Skills](#skills) or [Client tools](#client-tools) table, run `python3 scripts/check_library.py`, and open a pull request saying what it is for and how you tried it. One skill or tool per pull request. Skills here are Apache-2.0; use made-up names and data in examples, and keep secrets out of files. The [guide](docs/writing-a-skill.md#7-trying-it-then-contributing-it) says how to try a skill in your own traceflow first.

## License

Apache-2.0. See [LICENSE](LICENSE). The robot in the logo is drawn from [agent-robot-avatar](https://www.npmjs.com/package/agent-robot-avatar), MIT; see [its licence](assets/LICENSE-agent-robot-avatar).
