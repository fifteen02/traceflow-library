# Writing a client tool

A client tool is a tool an agent calls and the person's client draws: a question to answer, options to pick from, a plan, a table, a chart. The agent sees its name, description and parameters like any tool's. When it calls one, the call goes to the client: the chat app draws a card, a channel such as WhatsApp sends text, buttons or a file. A tool that asks something waits for the person's answer and returns it as the call's result; a tool that only shows returns at once.

This guide goes from the definition to a pull request:

1. [Asks or shows](#1-asks-or-shows)
2. [The definition](#2-the-definition)
3. [Parameters and reply](#3-parameters-and-reply)
4. [What a client draws](#4-what-a-client-draws)
5. [Examples](#5-examples)
6. [Ids, namespaces and versions](#6-ids-namespaces-and-versions)
7. [A skill that needs it](#7-a-skill-that-needs-it)
8. [Trying it, then contributing it](#8-trying-it-then-contributing-it)

All the names in the examples are made up.

## 1. Asks or shows

| Kind | `rendersOnly` | `reply` | Examples |
|---|---|---|---|
| Asks | `false` | The schema of the person's answer | `ask`, `choose`, `confirm`, `collect` |
| Shows | `true` | None | `show_table`, `show_places`, `render_vega` |

Before writing one, look at the [client tools](../README.md#client-tools) traceflow has: most new needs are one of them with better arguments. A tool that shows something a channel can't draw well (a layout, a live chart) can be `app`-only (see [Channels](#channels)).

## 2. The definition

```
client-tools/send_postcard/
├── tool.json
├── RENDERING.md
├── icon.svg
└── examples/
    └── good/
        └── from-lisbon.json
```

`tool.json`:

```json
{
  "id": "traceflow/send_postcard@1",
  "name": "send_postcard",
  "version": 1,
  "description": "Show the person a postcard to send: a photo of the workspace on the front, the message on the back, and who it goes to. Show a Send and a Change button. Reply with sent=true only when they press Send; put anything else they said in note.",
  "parameters": {
    "type": "object",
    "properties": {
      "photo": { "type": "string", "description": "The photo on the front, relative to the workspace, e.g. photos/lisbon.jpg" },
      "message": { "type": "string", "description": "The message on the back, at most 300 characters" },
      "to": { "type": "string", "description": "Who it goes to, as the person calls them, e.g. Ana" }
    },
    "required": ["photo", "message", "to"]
  },
  "reply": {
    "type": "object",
    "properties": {
      "sent": { "type": "boolean", "description": "Whether the person pressed Send" },
      "note": { "type": "string", "description": "Anything the person said instead" }
    },
    "required": ["sent"]
  },
  "rendersOnly": false,
  "channels": "all",
  "icon": "icon.svg"
}
```

| Field | Rule |
|---|---|
| `id` | `namespace/name@version`: the namespace (`traceflow` for a tool in this library, your own source's in your own repository), the folder's name, the major version. See [section 6](#6-ids-namespaces-and-versions). |
| `name` | The folder's name and what the model calls: lowercase letters, digits and underscores. |
| `version` | The major version, a whole number from 1. |
| `description` | What the model reads, and the spec a client implements. Say what it shows, what the person does, and what the reply is, in that order. Say when to use it and when a sentence is better. |
| `parameters` | The JSON Schema of the arguments, an object. Give every property a `description`. |
| `reply` | The JSON Schema of the person's answer. Left out for a tool that only shows. |
| `rendersOnly` | `true` for a tool that only shows, `false` for one that waits for an answer. |
| `channels` | `all` or `app` (below). |
| `icon` | The SVG in the folder its card is drawn with, `icon.svg` by convention (a folder's `icon.svg` is used when this is left out). Drawn as the [README's icons](../README.md#icons) are: traceflow's ink tile with one Ant Design outlined glyph in the library's gradient. At most 32 KB, and no script, style, image, link, `use`, handler or `url()` out of itself: traceflow refuses those, and `scripts/check_library.py` checks it. |

### Channels

- `all`: every client draws it. A channel without UI (WhatsApp, Telegram, email, a terminal) draws it as text, buttons or a file, and the tool must still make sense there. Most tools are `all`.
- `app`: only a client that says it draws it is offered the tool, never a channel. A harness may declare an `app` tool only where its config says the client draws it. `render_a2ui` is the one today.

## 3. Parameters and reply

- Keep arguments flat and named for what they are (`summary`, `options`, `to`), not how they are drawn.
- Mark optional what a client can do without, and say in its description what happens when it is left out ("Yes when left out").
- A reply is what the person did, not what the client drew: `{"choice": "Lisbon"}`, never a button's id.
- traceflow reads a few extension keys in a reply schema; keep them in `tool.json` as they are:

| Key | On | Means |
|---|---|---|
| `x-pick-from` | A reply field | The argument it picks from (`"suggestions"`): a client offers those values. |
| `x-pick-only` | Beside `x-pick-from` | The answer must be one of them: a client offers a fixed choice. |
| `x-pick-min`, `x-pick-max` | A list field picking several | The arguments holding the fewest and the most to pick. |
| `x-schema-from` | The reply | The argument that is itself the reply's schema (`collect`'s `schema`). |
| `secret`, `sensitive` | A field | Typed masked, kept only as a handle, never shown back. |

A reply that is one required text field (`{"answer"}`) can be answered by a typed line on any channel. Any other reply needs buttons the channel can draw, or a form: say in RENDERING.md what a channel does instead.

## 4. What a client draws

`RENDERING.md` is short and factual. Four parts:

```markdown
# send_postcard

The photo on the front, the message on the back, who it goes to, and Send and Change buttons.

## Reply

`{"sent", "note"?}`: `sent` is true only when the person pressed Send.

## In traceflow's apps

A shell in the agent's colour around the photo, the message beneath it, Send as the primary button.

## On a channel without UI

The photo attached, the message as text, and buttons Send and Change; a channel without buttons asks "Reply send or change".
```

- **What it shows**: every argument and where it goes.
- **Reply**: what comes back, and when.
- **In traceflow's apps**: what the chat app draws (its components are in traceflow's `frontend/traceflow-chat/DESIGN.md`). A tool the chat app has no card for is drawn by its Fallback card, the arguments as labelled fields.
- **On a channel without UI**: the text, buttons or file a channel sends, and how a typed answer is read. A channel shows any tool it has no drawing for as its arguments in labelled fields; say when that is enough.

## 5. Examples

Each example is one call: its arguments at the top level, with notes beside them that are not arguments.

```json
{
  "asked": "Send Ana a postcard from Lisbon.",
  "why": "A photo the person took, a short message, one person.",
  "photo": "photos/lisbon.jpg",
  "message": "Sunny all week. The custard tarts are as good as you said.",
  "to": "Ana"
}
```

| Note | Means |
|---|---|
| `asked` | What the person asked, that led to the call. |
| `said` | What the agent said with it. |
| `why` | Why this call is right (good) or wrong (bad). |
| `expect` | Bad examples only: a piece of the line the refusal says. |

- `examples/good/` holds calls that pass: at least one, realistic, with made-up names.
- `examples/bad/` holds calls a tool's checks refuse, each with `why` and `expect`, when the tool has checks of its own (`render_vega`, `render_a2ui`).
- `scripts/check_library.py` checks every example's keys against the parameters, its required ones there.

## 6. Ids, namespaces and versions

- An id is `namespace/name@major`. Names are for the model; ids are for everything else: calls, the trace, checks, renderers and skills.
- A namespace is a source an admin trusts. `traceflow` is this library and is reserved: a tool you author takes your namespace (your account's, `mark/…`, or your team's source, `acme/…`). A team publishes its tools from its own repository, laid out like this one.
- When two tools offered to one agent have the same name, `traceflow`'s keeps the plain name and the other is qualified (`acme__send_postcard` beside `traceflow`'s `send_postcard`).
- **A breaking change bumps the major**: a parameter removed, renamed or newly required; a reply field removed, renamed or changing meaning. Write it as `@2` in the same folder (`"version": 2`). Adding an optional parameter or improving a description keeps the major.
- One major per tool per harness. Apps keep a renderer per major, so old threads draw as they did.

## 7. A skill that needs it

A skill that can't work without a client tool pins it by id in its header:

```yaml
metadata:
  traceflow:
    tools: [render_vega, execute]
    requires:
      tools: [traceflow/render_vega@1]
```

- `tools` lists names, as the model calls them. `requires.tools` lists ids: the skill is offered only where that definition, at that major, is.
- The skill links to the tool's folder for its definition and examples; it never copies the tool. A file the skill's scripts read at run time stays in the skill, because a skill is installed on its own: the a2ui skill keeps a copy of `client-tools/render_a2ui/catalog.json`, and `scripts/check_library.py` fails when the two differ.

## 8. Trying it, then contributing it

Try the tool in a traceflow of your own: on the **Tools** page, **New Client Tool**, with the same name, description and schemas. Give it to an agent, ask the questions it is for, and answer it in the chat app and on a channel.

To contribute it:

1. Fork this repository and make a branch.
2. Add the tool as one folder under `client-tools/`, named as its `name`, with `tool.json`, `RENDERING.md` and its examples.
3. Add a row for it to the [Client tools](../README.md#client-tools) table.
4. Run `python3 scripts/check_library.py`; it must say `all passed`.
5. Open a pull request saying what the tool is for, how each client draws it, and how you tried it.

Tools here are Apache-2.0, like the repository: by contributing, you license your tool under it. Use made-up names and data in examples, and keep secrets out.
