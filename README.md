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

## License

Apache-2.0. See [LICENSE](LICENSE).
