# Writing a skill

A skill teaches a traceflow agent how to do one kind of task well. It is a folder with a `SKILL.md` in it: a short header, then instructions for the agent. On every turn the agent sees each skill's `name` and `description`. When a task needs one, it calls `load_skill`, reads the instructions, and follows them with the tools it has.

This guide goes from the simplest skill up:

1. [The tools an agent can have](#1-the-tools-an-agent-can-have)
2. [What the skill computer already has](#2-what-the-skill-computer-already-has)
3. [The header](#3-the-header)
4. [Four kinds of skill](#4-four-kinds-of-skill): text only, with Python packages, with programs, with both
5. [Settings](#5-settings)
6. [The icon](#6-the-icon)
7. [Trying it, then contributing it](#7-trying-it-then-contributing-it)

traceflow never guesses what a skill needs. A skill declares the tools it uses, the programs it runs and the Python packages it imports. traceflow installs only what is declared, and says at install what the skill uses but doesn't declare. All the names in the examples are made up.

## 1. The tools an agent can have

A skill doesn't give an agent tools: the admin does, per agent. A skill says which tools it uses (`metadata.traceflow.tools`, below), so the admin can see at install whether the agent has them. Use these names:

| Group | Tools | What they do |
|---|---|---|
| Skills | `load_skill` | Reads a skill's instructions. Every agent with a skill has it; don't list it. |
| | `fetch_skill` | Downloads a skill into the workspace (`skills-to-review/<name>/`) to review it before installing, with what the install check finds. Admins only. |
| Workspace | `ls`, `glob`, `grep`, `read_file`, `write_file`, `edit_file` | Lists, finds, reads and writes files in the agent's workspace, a skill's files included (`.skills/<name>/`). |
| | `execute` | Runs a command. With `skill` set to a skill's name, it runs in that skill's computer (see [below](#2-what-the-skill-computer-already-has)). |
| Everyday | `current_time`, `working_days`, `calculate`, `convert_units` | The date and time in a time zone, working days between two dates, exact arithmetic, converting kitchen amounts. |
| Preferences | `remember_preference`, `list_preferences`, `forget_preference` | Keeps what the person said they prefer, across conversations. |
| Messages | `search_messages`, `search_messages_thread` | Searches the person's own messages and emails; reads a found message in its thread. |
| Email | `gmail_send` | Sends an email from the person's own mailbox. |
| Calendar | `calendar_list_events`, `calendar_find_free_time`, `calendar_create_event`, `calendar_update_event`, `calendar_delete_event` | Reads and changes the person's calendar. |
| Drive | `drive_search`, `drive_read`, `drive_save`, `drive_set_visibility` | Finds, reads and saves files in the person's drive, and sets who can see one. |
| Team chat | `send_slack_message` | Posts a message to a channel or a person. |
| Connected servers | `mcp__<server>__<tool>` | A tool from a server the admin connected, by its server's name and its own. |

Which of these an agent has depends on what the admin connected and gave it. Write the skill so it says what to do when a tool it would like is missing.

## 2. What the skill computer already has

A skill with scripts runs them in a **skill computer**: a container beside the agent, built once at install, never while the agent runs. It starts from a base that already has:

- **Programs:** `python3`, `pip`, `bash`, `sh`, `curl`, `wget`, `jq`, `git`, `ffmpeg`, `ffprobe`, `zip`, `unzip`, `7z`, `bc`, `rg`, `sqlite3`, `pdftotext`, `pdftoppm`, `pdfinfo`, `pdfimages`, `qpdf`, `tesseract`, `pandoc`, `convert`, `gs`, `soffice`, `node`, `npm`, `npx`, `markitdown`, `yt-dlp`, `uv`, `playwright`.
- **Python packages:** `pandas`, `numpy`, `scipy`, `scikit-learn`, `statsmodels`, `matplotlib`, `seaborn`, `pyarrow`, `openpyxl`, `xlsxwriter`, `xlrd`, `pillow`, `python-pptx`, `python-docx`, `pypdf`, `pdfplumber`, `pypdfium2`, `pdf2image`, `reportlab`, `img2pdf`, `sympy`, `tqdm`, `python-dateutil`, `pytz`, `markitdown`, `lxml`, `beautifulsoup4`, `requests`, `pyyaml`, `yt-dlp`, `playwright`, and the standard library.

Declare only what goes beyond these: a program in `metadata.traceflow.requires.bins`, a Python package in `requirements.txt`. The admin can also add packages to an environment that all its skills share.

## 3. The header

```yaml
---
name: reply-drafts
description: How to draft a reply to one of the person's messages or emails in their own voice. Use it when they ask you to answer, reply to, write back to or get back to someone, or to say no politely. Not for writing new emails from scratch.
license: Apache-2.0
compatibility: Needs the person's messages and emails to be connected.
metadata:
  icon: icon.svg
  author: your-github-handle
  traceflow:
    tools: [search_messages, search_messages_thread]
---
```

| Field | Rule |
|---|---|
| `name` | Required. 1–64 characters: lowercase letters, digits and single hyphens, not at the start or end. The same as the folder's name. |
| `description` | Required, at most 1024 characters. See below. |
| `license` | `Apache-2.0` for skills in this repository. |
| `compatibility` | Optional. What the skill needs from the person or the admin, in words: an account connected, internet access. |
| `metadata.icon` | The icon's file in the folder (see [The icon](#6-the-icon)). Left out, traceflow looks for `icon.svg`. |
| `metadata.always` | Optional. `true` suggests the whole skill is read on every turn. Keep it for skills most turns need; the admin decides in the end. |
| `metadata.author` | Optional. Your GitHub handle or your project's name. |
| `metadata.traceflow.tools` | The tools the instructions use, by the names in [section 1](#1-the-tools-an-agent-can-have). |
| `metadata.traceflow.requires.bins` | The programs the scripts run that the skill computer lacks. |
| `metadata.traceflow.requires.env` | The settings the scripts read (see [Settings](#5-settings)). |

Write any other key under `metadata`. A top-level key not in the table is ignored, with a warning.

**The `description`** is all the agent knows about a skill until it loads it, so it decides whether the skill is ever used. Say what the skill is for and, above all, **when** to use it, in the words a person would use: "Use it when they ask you to answer, reply to, write back to…". Say when not to use it if another skill is close. Leave out how it works; that is the body's job. Avoid `: ` (a colon and a space) in a header value, or put the whole value in quotes.

**The body** is read only when the skill is loaded, so it can be longer, but it is read in full each time. Write it for the agent:

- start with the rules that always hold ("Never send anything");
- then one short recipe per kind of question, each with a heading that quotes how a person asks it, and numbered steps naming the exact tools and arguments;
- say what to do when a step finds nothing, finds more than one answer, or a tool is missing;
- leave out what the agent knows already.

## 4. Four kinds of skill

| Kind | Its folder | It declares | The agent |
|---|---|---|---|
| [Text only](#41-text-only) | `SKILL.md`, `icon.svg`, any `.md` files | Its tools | Reads the instructions and the files they link to |
| [With Python packages](#42-with-python-packages) | and `scripts/`, `requirements.txt` | Its tools; its packages in `requirements.txt` | Runs the scripts with `execute` |
| [With programs](#43-with-programs) | and `scripts/` | Its tools; its programs in `requires.bins` | Runs the scripts with `execute` |
| [With both](#44-with-both) | and `scripts/`, `requirements.txt` | All three | Runs the scripts with `execute` |

### 4.1 Text only

Instructions and nothing to install. Most skills are this kind.

```
skills/reply-drafts/
├── SKILL.md
├── icon.svg
└── tone.md           how the person writes, per kind of chat
```

```markdown
---
name: reply-drafts
description: How to draft a reply to one of the person's messages or emails in their own voice. Use it when they ask you to answer, reply to, write back to or get back to someone, or to say no politely. Not for writing new emails from scratch.
license: Apache-2.0
compatibility: Needs the person's messages and emails to be connected.
metadata:
  icon: icon.svg
  author: your-github-handle
  traceflow:
    tools: [search_messages, search_messages_thread, read_file]
---

# Drafting replies

Never send anything. Write the draft, show it, and wait for the person to say it is right.

## Pick the recipe for the question

### A reply to one message ("reply to Ana")

1. Find the message with `search_messages` (`person` set to Ana) and read it in its thread with `search_messages_thread`.
2. Read [tone.md](tone.md) for the kind of chat (family, friends, work), then two or three of the person's own earlier messages in that chat, to match how they write there.
3. Answer every question the message asks. Say what you could not answer and why.

### Saying no politely

1. Thank them, say no in the first two sentences, and give one reason at most.
2. Offer another time or another way when the person has given you one. Never make one up.
```

**Files.** Put what is long, or needed only some of the time, in its own file and link to it with a path from the folder (`[tone.md](tone.md)`). The agent reads it with `read_file` from `.skills/<name>/`. Every link in a `.md` file must lead to a file in the folder; traceflow warns at install when one doesn't. Any kind of skill can have files.

### 4.2 With Python packages

A Python script, with a package the skill computer lacks.

```
skills/qr-codes/
├── SKILL.md
├── icon.svg
├── requirements.txt
└── scripts/
    └── make_qr.py
```

```markdown
---
name: qr-codes
description: Makes a QR code image for a link, a Wi-Fi network or any short text. Use it when the person asks for a QR code, or for a way to share a link or a network that others can scan.
license: Apache-2.0
metadata:
  icon: icon.svg
  author: your-github-handle
  traceflow:
    tools: [execute]
---

# QR codes

Run the script with `execute`, with `skill` set to `qr-codes`. It writes a PNG into the workspace and prints its path:

    python3 .skills/qr-codes/scripts/make_qr.py "https://example.com/menu" --out qr/menu.png

- For a Wi-Fi network, the text is `WIFI:T:WPA;S:<network>;P:<password>;;`. Use only a network and a password the person gave you.
- Name the file after what it is for (`qr/wifi-home.png`) and tell the person its path.
```

`requirements.txt`, one package a line, with the version you tested:

```
qrcode==8.0
```

`scripts/make_qr.py`:

```python
import argparse

import qrcode


def main():
    parser = argparse.ArgumentParser(description="Make a QR code image.")
    parser.add_argument("text")
    parser.add_argument("--out", required=True, help="the PNG to write, in the workspace")
    args = parser.parse_args()
    qrcode.make(args.text).save(args.out)
    print(args.out)


if __name__ == "__main__":
    main()
```

How it fits together:

- **Running it.** Commands start in the workspace's root, so the body names the script by its path from there: `.skills/<name>/scripts/…`. With `skill` set, `execute` runs the command in the skill computer, beside the skill's files. Files for the person go in the workspace (`qr/menu.png`), never in the skill's folder.
- **`requirements.txt`.** At the folder's root. List every package the scripts import that the skill computer lacks, one per line with the version you tested. Only package lines are accepted: a name, its extras, versions and markers, and `#` notes. Options (`-e`, `-r`, `--index-url`), URLs, `git+` and paths are refused. Every line must install, or the install fails and says why.
- **An import nothing covers** is reported at install, with the line to add, and isn't installed. Here `qrcode` needs Pillow to write the PNG, which the skill computer has.

### 4.3 With programs

A shell script that runs a program the skill computer lacks.

```
skills/photo-details/
├── SKILL.md
├── icon.svg
└── scripts/
    └── photo_details.sh
```

```markdown
---
name: photo-details
description: When, where and with what a photo was taken, from the details saved inside it. Use it when the person asks when or where a photo in their workspace was taken, or which camera or phone took it.
license: Apache-2.0
metadata:
  icon: icon.svg
  author: your-github-handle
  traceflow:
    tools: [execute, glob]
    requires:
      bins: [exiftool]
---

# Photo details

1. Find the photo with `glob` when the person names it loosely ("the beach photo").
2. Run the script with `execute`, with `skill` set to `photo-details`:

       sh .skills/photo-details/scripts/photo_details.sh photos/beach.jpg

   It prints JSON: the time it was taken, its latitude and longitude, the camera's make and model, and its size.
3. Answer only what was asked. Give a place only when the person asked where, and say a photo without those details has none saved.
```

`scripts/photo_details.sh`:

```bash
#!/bin/sh
# When and where a photo was taken, and with what, as JSON.
exec exiftool -json -n -DateTimeOriginal -GPSLatitude -GPSLongitude -Make -Model -ImageWidth -ImageHeight "$@"
```

- **`requires.bins`** lists the programs the scripts run that the skill computer lacks. traceflow installs each from a list of programs it knows; one it doesn't know is reported at install, and the skill can't run until the admin's environment has it.
- **A program a script runs but the list leaves out** is reported at install when the skill computer lacks it, and isn't installed.

### 4.4 With both

A Python package that drives a program: here, drawing diagrams with Graphviz.

```
skills/diagrams/
├── SKILL.md
├── icon.svg
├── requirements.txt
└── scripts/
    └── draw.py
```

```markdown
---
name: diagrams
description: Draws a diagram as an image, such as a family tree, a plan with its steps, or who reports to whom. Use it when the person asks for a diagram, a chart of how things connect, or a picture of a process.
license: Apache-2.0
metadata:
  icon: icon.svg
  author: your-github-handle
  traceflow:
    tools: [write_file, execute]
    requires:
      bins: [dot]
---

# Diagrams

1. Write the diagram in Graphviz's DOT language with `write_file`, into the workspace (`diagrams/plan.dot`). Keep labels short; put the details in your answer.
2. Draw it with `execute`, with `skill` set to `diagrams`:

       python3 .skills/diagrams/scripts/draw.py diagrams/plan.dot --out diagrams/plan.png

3. If it fails, the error names the line of the DOT text to fix. Fix it and draw again, at most twice.
```

`requirements.txt`:

```
graphviz==0.20.3
```

`scripts/draw.py`:

```python
import argparse

import graphviz


def main():
    parser = argparse.ArgumentParser(description="Draw a DOT file as an image.")
    parser.add_argument("source", help="the .dot file, in the workspace")
    parser.add_argument("--out", required=True, help="the image to write: .png, .svg or .pdf")
    args = parser.parse_args()
    print(graphviz.render("dot", filepath=args.source, outfile=args.out))


if __name__ == "__main__":
    main()
```

The Python package (`graphviz`, in `requirements.txt`) only drives the program (`dot`, in `requires.bins`). Leave out either, and the install says which is missing.

## 5. Settings

A script that needs a value from the admin, such as an address or a key, reads it from its environment. Declare each one:

```yaml
metadata:
  traceflow:
    requires:
      env: [WEATHER_API_URL, WEATHER_API_KEY]
    primaryEnv: WEATHER_API_KEY
```

- Each becomes a setting the admin fills in at install. `primaryEnv` is the main one, if any.
- A setting whose name has a word like `KEY`, `TOKEN`, `SECRET` or `PASSWORD` is kept secret and masked.
- A name can't be `PATH`, `HOME` or another the skill computer sets itself, or start with `LD_` or `PYTHON`.
- A skill computer has no network unless the admin gives it one. Say in `compatibility` when the skill needs the internet.
- Never put a key in a file of the skill.

## 6. The icon

Draw it in the style of the set (see [Icons](../README.md#icons)). The smallest icon that fits:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" role="img" aria-label="Reply drafts">
  <path d="M32 0C58 0 64 6 64 32S58 64 32 64 0 58 0 32 6 0 32 0Z" fill="#12A594"/>
  <path d="M17 13h30a8 8 0 0 1 8 8v13a8 8 0 0 1-8 8H30l-10 8v-8h-3a8 8 0 0 1-8-8V21a8 8 0 0 1 8-8z" fill="#FFFFFF"/>
  <ellipse cx="25.5" cy="24.5" rx="3.6" ry="3.87" fill="#12A594"/>
  <ellipse cx="38.5" cy="24.5" rx="3.6" ry="3.87" fill="#12A594"/>
  <path d="M26.5 32q5.5 4.7 11 0" fill="none" stroke="#12A594" stroke-width="3" stroke-linecap="round"/>
</svg>
```

traceflow draws an icon as an image, so it runs nothing. It still refuses one that:

- holds a `<script>`, `<style>`, `<image>`, `<use>`, `<foreignObject>`, `<a>`, `<iframe>`, `<embed>`, `<object>` or `<feImage>` element (style with attributes, as above, not CSS);
- has an event handler (`onload`, `onclick`, …);
- links out of itself: an `href` or `url()` must point inside the file (`url(#tile)`), never to a file or a web address;
- has a `<!DOCTYPE>`, isn't well-formed XML with `<svg>` at its root, or is larger than 32 KB.

A refused icon is left off the card, with a warning at install; the skill still works.

## 7. Trying it, then contributing it

Install your skill in a traceflow of your own, from the **Skills** page:

- **From a git repository**: your fork's URL, your branch as the **Ref**, and the skill's folder (`skills/qr-codes`).
- **Upload a zip**: a zip of the folder, or of what is in it, with `SKILL.md` at its root.

The install shows the header as traceflow read it, the tools, programs and packages the skill declares, and what is missing: a tool the agent lacks, an import or a program nothing installs, a broken link, a refused icon. Then give the skill to an agent and ask it the questions your recipes are for. Install it again after each change.

To contribute it:

1. Fork this repository and make a branch.
2. Add your skill as one folder under `skills/`, named as its `name`. One skill per folder, and one skill per pull request.
3. Add a row for it to the [Skills](../README.md#skills) table.
4. Open a pull request saying what the skill is for and how you tried it.

Skills here are Apache-2.0, like the repository: by contributing, you license your skill under it. Use made-up names and data in examples (Ana, Lisbon, `example.com`), never a real person's details, and keep secrets out: a key belongs in a setting, never in a file.
