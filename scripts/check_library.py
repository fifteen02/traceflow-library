"""Check the library as a whole: its client tools, the skills' pins on them, and the copies a skill keeps.

    python3 scripts/check_library.py

- every folder under client-tools/ has a tool.json that reads, with the keys a definition needs, its id
  `traceflow/<folder>@<version>`, a RENDERING.md, and at least one good example;
- every example's keys are the tool's parameters (or notes: asked, said, why, expect), its required ones there; a bad
  one says why and what it expects;
- render_a2ui's and render_vega's examples pass (good) or fail with their expect (bad) under the skills' validators;
- every id a skill pins in metadata.traceflow.requires.tools is a client tool here at that major (a bare name isn't
  pinned: noted, not checked);
- the a2ui skill's catalog.json is client-tools/render_a2ui/catalog.json;
- every client tool has an icon (tool.json's icon, else its folder's icon.svg) traceflow would draw: an SVG of at most
  32 KB with no DOCTYPE, script, style, image, link, use, handler or url() out of itself (as SkillIcon refuses).

Standard library only. Prints a line per check and exits 1 when any fails.
"""

import json
import xml.etree.ElementTree as ElementTree
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "client-tools"
SKILLS = ROOT / "skills"
NAMESPACE = "traceflow"
"""The library's own namespace: every tool here is traceflow/<name>@<major>."""
KEYS = {"id", "name", "version", "description", "parameters", "reply", "rendersOnly", "channels", "icon"}
REQUIRED = KEYS - {"reply", "icon"}
CHANNELS = {"all", "app"}
NOTES = {"asked", "said", "why", "expect"}
"""Keys an example may carry beside the call's arguments: what was asked, what was said with it, why, what it gets."""
ID = re.compile(r"^([a-z0-9][a-z0-9-]*)/([a-z0-9_]+)@([1-9][0-9]*)$")
VALIDATORS = {"render_a2ui": SKILLS / "a2ui" / "scripts" / "validate.py",
              "render_vega": SKILLS / "vega-lite" / "scripts" / "validate.py"}
"""The tools whose examples a skill's validator runs, and that validator."""

ICON = "icon.svg"
"""The icon a tool's folder has when its tool.json names none."""
ICON_MAX_BYTES = 32 * 1024
"""SkillIcon.MAX_BYTES: the largest icon traceflow keeps."""
ICON_REFUSED = {"script", "foreignobject", "image", "iframe", "embed", "object", "use", "a", "feimage", "style"}
"""SkillIcon.REFUSED: elements an icon never has, what runs, embeds or reaches out."""
LOCAL_URL = re.compile(r"(?s).*url\(\s*#[^)]*\).*")

failed = 0


def report(passed, line):
    global failed
    print(("PASS " if passed else "FAIL ") + line)
    failed += not passed


def read_json(path):
    """path's JSON, or None and a FAIL when it doesn't read."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as unreadable:
        report(False, str(path.relative_to(ROOT)) + ": doesn't read as JSON: " + str(unreadable))
        return None


def check_tool(folder):
    """One client tool's folder: its definition, its RENDERING.md, its examples. Its definition, or None."""
    where = "client-tools/" + folder.name
    tool = read_json(folder / "tool.json") if (folder / "tool.json").exists() else None
    if tool is None:
        report(False, where + ": no tool.json")
        return None
    problems = []
    if not isinstance(tool, dict):
        problems.append("tool.json isn't an object")
        tool = {}
    problems += ["no " + key for key in sorted(REQUIRED - set(tool))]
    problems += ["unknown key " + key for key in sorted(set(tool) - KEYS)]
    if tool.get("name") != folder.name:
        problems.append("name " + json.dumps(tool.get("name")) + " isn't the folder's")
    version = tool.get("version")
    if not (isinstance(version, int) and not isinstance(version, bool) and version >= 1):
        problems.append("version " + json.dumps(version) + " isn't a whole number from 1")
    expected = NAMESPACE + "/" + folder.name + "@" + str(version)
    if tool.get("id") != expected:
        problems.append("id " + json.dumps(tool.get("id")) + " isn't " + json.dumps(expected))
    if not isinstance(tool.get("description"), str) or not tool.get("description", "").strip():
        problems.append("no description")
    parameters = tool.get("parameters")
    if not (isinstance(parameters, dict) and parameters.get("type") == "object"):
        problems.append("parameters isn't an object's schema")
    if not isinstance(tool.get("rendersOnly"), bool):
        problems.append("rendersOnly isn't true or false")
    elif tool["rendersOnly"] == ("reply" in tool):
        problems.append("a tool that only shows has no reply, any other has one" if tool["rendersOnly"]
                        else "a tool that answers needs a reply schema")
    if "reply" in tool and not isinstance(tool["reply"], dict):
        problems.append("reply isn't a schema")
    if tool.get("channels") not in CHANNELS:
        problems.append("channels " + json.dumps(tool.get("channels")) + " isn't one of all, app")
    if not (folder / "RENDERING.md").exists():
        problems.append("no RENDERING.md")
    if not list((folder / "examples" / "good").glob("*.json")):
        problems.append("no good example")
    report(not problems, where + "/tool.json: " + (tool.get("id", "?") if not problems else "; ".join(problems)))
    return tool if not problems else None


def local(name):
    """An element's or attribute's name without its namespace, lower-cased, as SkillIcon reads it."""
    return name.rsplit("}", 1)[-1].rsplit(":", 1)[-1].lower()


def icon_refusal(path):
    """Why traceflow wouldn't draw the SVG at path as an icon (SkillIcon.refusal); None when it would."""
    if not path.name.lower().endswith(".svg"):
        return "an icon is an SVG"
    data = path.read_bytes()
    if len(data) > ICON_MAX_BYTES:
        return "it is over " + str(ICON_MAX_BYTES // 1024) + " KB"
    if b"<!DOCTYPE" in data.upper():
        return "it doesn't read as SVG (it has a DOCTYPE)"
    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError:
        return "it doesn't read as SVG"
    if local(root.tag) != "svg":
        return "it isn't an SVG"
    for element in root.iter():
        if not isinstance(element.tag, str):
            continue
        if local(element.tag) in ICON_REFUSED:
            return "it has a " + local(element.tag) + " element"
        for key, value in element.attrib.items():
            name, value = local(key), value.strip().lower()
            if name.startswith("on"):
                return "it has a " + name + " handler"
            if name == "href" and not value.startswith("#"):
                return "it links out of itself"
            if "url(" in value and not LOCAL_URL.match(value):
                return "it reaches out with url()"
    return None


def check_icon(folder, tool):
    """The tool's icon: the one its tool.json names, else its folder's icon.svg; one every tool has."""
    named = tool.get("icon")
    where = "client-tools/" + folder.name
    if named is not None and not (isinstance(named, str) and named.strip()):
        report(False, where + "/tool.json: icon " + json.dumps(named) + " isn't a file's name")
        return
    path = folder / (named.strip() if named else ICON)
    if not path.is_file() or folder.resolve() not in path.resolve().parents:
        report(False, where + ": no icon" + (" (tool.json names " + named + ")" if named else " (" + ICON + ")"))
        return
    why = icon_refusal(path)
    report(why is None, where + "/" + path.name + (": an icon traceflow draws" if why is None
                                                  else " isn't used as the icon: " + why))


def check_examples(folder, tool):
    """Each example's keys against the tool's parameters; a bad one's why and expect."""
    properties = set((tool["parameters"].get("properties") or {}))
    required = set(tool["parameters"].get("required") or [])
    problems, count = [], 0
    for kind in ("good", "bad"):
        for path in sorted((folder / "examples" / kind).glob("*.json")):
            count += 1
            example = read_json(path)
            if not isinstance(example, dict):
                problems.append(kind + "/" + path.name + " isn't an object")
                continue
            arguments = set(example) - NOTES
            unknown = sorted(arguments - properties)
            missing = sorted(required - arguments)
            if unknown:
                problems.append(kind + "/" + path.name + ": not a parameter: " + ", ".join(unknown))
            if missing:
                problems.append(kind + "/" + path.name + ": missing " + ", ".join(missing))
            if kind == "bad" and not (example.get("why") and example.get("expect")):
                problems.append(kind + "/" + path.name + ": a bad example says why and expect")
    report(not problems, "client-tools/" + folder.name + "/examples: " + str(count) + " calls fit the parameters"
           if not problems else "client-tools/" + folder.name + "/examples: " + "; ".join(problems))


def run_validator(name, folder):
    """The tool's examples under its skill's validator: good ones pass, bad ones fail with their expect."""
    validator = VALIDATORS[name]
    if not validator.exists():
        report(False, name + ": no validator at " + str(validator.relative_to(ROOT)))
        return
    problems, count = [], 0
    for kind in ("good", "bad"):
        for path in sorted((folder / "examples" / kind).glob("*.json")):
            count += 1
            done = subprocess.run([sys.executable, str(validator), str(path)], capture_output=True, text=True)
            lines = done.stdout.strip().splitlines()
            if kind == "good" and not (done.returncode == 0 and lines and lines[0].startswith("ok")):
                problems.append("good/" + path.name + " refused: " + (lines[0] if lines else done.stderr.strip())[:120])
            if kind == "bad":
                expect = (read_json(path) or {}).get("expect", "")
                if not (done.returncode == 1 and any(expect in line for line in lines)):
                    problems.append("bad/" + path.name + ": expected \"" + expect + "\", got: "
                                    + (lines[0] if lines else "ok")[:120])
    report(not problems, name + ": " + str(count) + " examples pass or fail as they say under "
           + str(validator.relative_to(ROOT)) if not problems else name + ": " + "; ".join(problems))


def header(path):
    """A SKILL.md's YAML header as nested dicts: keys, inline [a, b] lists and block - lists (all this library uses)."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    root = {}
    stack = [(-1, root)]
    listing = None
    """The key a run of - lines belongs to: (its mapping, its name), while they come."""
    for line in text[4:].split("\n---", 1)[0].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        body = line.strip()
        if body.startswith("- ") and listing is not None:
            mapping, key = listing
            if not isinstance(mapping[key], list):
                mapping[key] = []
                stack.pop()
            mapping[key].append(body[2:].strip().strip("'\""))
            continue
        listing = None
        while indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        key, _, value = body.partition(":")
        value = value.strip()
        if not value:
            parent[key] = {}
            stack.append((indent, parent[key]))
            listing = (parent, key)
        elif value.startswith("[") and value.endswith("]"):
            parent[key] = [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
        else:
            parent[key] = value.strip("'\"")
    return root


def requires_tools(path):
    """The tools a skill can't do without: its metadata.traceflow.requires.tools."""
    node = header(path)
    for key in ("metadata", "traceflow", "requires", "tools"):
        node = node.get(key) if isinstance(node, dict) else None
    return node if isinstance(node, list) else []


def check_skill(path, tools_by_id):
    skill = path.parent.name
    for entry in requires_tools(path):
        pinned = ID.match(entry)
        if not pinned:
            print("NOTE skills/" + skill + " requires " + json.dumps(entry) + " by name only: not pinned")
            continue
        namespace, name, major = pinned.groups()
        if namespace != NAMESPACE:
            report(False, "skills/" + skill + " requires " + entry + ": not this library's namespace (" + NAMESPACE + ")")
        elif entry not in tools_by_id:
            here = next((tool_id for tool_id in tools_by_id if tool_id.startswith(namespace + "/" + name + "@")), None)
            report(False, "skills/" + skill + " requires " + entry + ": no such client tool"
                   + (" (client-tools/" + name + " is " + here + ")" if here else ""))
        else:
            report(True, "skills/" + skill + " requires " + entry + ": client-tools/" + name)


def main():
    tools_by_id = {}
    for folder in sorted(path for path in TOOLS.iterdir() if path.is_dir()):
        tool = check_tool(folder)
        if tool is None:
            continue
        tools_by_id[tool["id"]] = tool
        check_examples(folder, tool)
        check_icon(folder, tool)
        if folder.name in VALIDATORS:
            run_validator(folder.name, folder)
    for path in sorted(SKILLS.glob("*/SKILL.md")):
        check_skill(path, tools_by_id)
    ours, theirs = SKILLS / "a2ui" / "catalog.json", TOOLS / "render_a2ui" / "catalog.json"
    same = ours.exists() and theirs.exists() and ours.read_bytes() == theirs.read_bytes()
    report(same, "skills/a2ui/catalog.json is client-tools/render_a2ui/catalog.json"
           + ("" if same else ": copy the tool's over the skill's"))
    print(str(len(tools_by_id)) + " client tools; " + ("all passed" if not failed else str(failed) + " failed"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
