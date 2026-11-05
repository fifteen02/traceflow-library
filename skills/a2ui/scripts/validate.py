"""Check an A2UI surface the way render_a2ui will, before sending it.

    python3 validate.py surface.json     (or - to read it from stdin)

The file is render_a2ui's arguments ({"messages": [...]}), the messages list, the one createSurface message, or one of
render_a2ui's examples or this skill's layouts. Prints "ok", or one problem per line. Exits 0 when the surface can be drawn, 1 when not.

A copy, in Python, of traceflow's A2uiSurfaces and A2uiCatalog (the source of truth, in the traceflow repo:
backend/traceflow-parent/traceflow-effects/traceflow-tools/src/main/java/com/fifteen02/traceflow/tool/generative/),
with the same rules, limits and wording. It reads catalog.json from the skill's folder, a copy of the library's
client-tools/render_a2ui/catalog.json, and checks each VegaChart's spec with vega_rules.py, beside this
script. It doesn't compile charts: validate_chart.py, beside it, does.
Standard library only.
"""

import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.setrecursionlimit(10000)
sys.path.insert(0, str(Path(__file__).resolve().parent))

import vega_rules  # noqa: E402  (beside this script)
from vega_rules import jstr  # noqa: E402

VERSION = "1.0"
"""The protocol version a surface is written in."""
MOST_COMPONENTS = 40
"""The most pieces one surface has."""
DEEPEST = 5
"""The deepest a surface's tree goes, its root the first level."""
MOST_BUTTONS = 4
"""The most buttons one surface offers."""

SURFACE_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")
COMMON = {"id", "catalogId", "accessibility", "metadata"}
"""What every component may have besides its piece's own properties (A2UI's ComponentCommon)."""
CATALOG = Path(__file__).resolve().parent.parent / "catalog.json"


class Catalog:
    """The pieces an agent may lay a reply out with (catalog.json), read by the few JSON Schema keywords it uses."""

    def __init__(self, catalog):
        self.id = catalog.get("catalogId")
        self.components = catalog.get("components") or {}
        self.defs = catalog.get("$defs") or {}

    @staticmethod
    def read(path=CATALOG):
        return Catalog(json.loads(Path(path).read_text(encoding="utf-8")))

    def pieces(self):
        return list(self.components)

    def check(self, kind, component, path, found):
        """What is wrong with component as a piece of kind, each problem said at path."""
        piece = self.components.get(kind)
        if not isinstance(piece, dict):
            found.append(path + ".component: there is no \"" + jstr(kind) + "\" piece; use one of " + ", ".join(self.pieces()))
            return
        properties = piece.get("properties") if isinstance(piece.get("properties"), dict) else {}
        for key in component:
            if key not in properties and key not in COMMON:
                found.append(path + "." + jstr(key) + ": a " + jstr(kind) + " has no " + jstr(key) + " (it has "
                             + ", ".join(jstr(k) for k in properties if k != "component") + ")")
        self.value(component, piece, path, found, True)

    def value(self, value, schema, path, found, own_keys):
        """value against schema: open (extra keys allowed) unless the schema closes it, or own_keys were checked."""
        ref = schema.get("$ref")
        if isinstance(ref, str):
            target = self.defs.get(ref[ref.rfind("/") + 1:])
            if isinstance(target, dict):
                self.value(value, target, path, found, False)
            return
        if "const" in schema and not same(schema["const"], value):
            found.append(path + ": must be " + jstr(schema["const"]))
            return
        kind = schema.get("type")
        if isinstance(kind, str) and not is_a(kind, value):
            found.append(path + ": must be " + article(kind) + ", not " + describe(value))
            return
        options = schema.get("enum")
        if isinstance(options, list) and not any(same(option, value) for option in options):
            found.append(path + ": \"" + jstr(value) + "\" isn't one of " + jstr(options))
        most = schema.get("maxLength")
        if isinstance(value, str) and is_number(most) and utf16(value) > int(most):
            found.append(path + ": " + str(utf16(value)) + " characters, more than " + jstr(most)
                         + "; say less, or in the reply's words")
        if is_number(value):
            least = schema.get("minimum")
            if is_number(least) and value < least:
                found.append(path + ": at least " + jstr(least))
            most = schema.get("maximum")
            if is_number(most) and value > most:
                found.append(path + ": at most " + jstr(most))
        if isinstance(value, list):
            least = schema.get("minItems")
            if is_number(least) and len(value) < int(least):
                found.append(path + ": at least " + jstr(least) + (" item" if int(least) == 1 else " items"))
            most = schema.get("maxItems")
            if is_number(most) and len(value) > int(most):
                found.append(path + ": " + str(len(value)) + " items, more than " + jstr(most))
            items = schema.get("items")
            if isinstance(items, dict):
                for i, item in enumerate(value):
                    self.value(item, items, path + "[" + str(i) + "]", found, False)
        if isinstance(value, dict):
            properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
            required = schema.get("required")
            if isinstance(required, list):
                for key in required:
                    if key not in value:
                        found.append(path + ": needs " + jstr(key))
            if not own_keys and schema.get("additionalProperties") is False:
                for key in value:
                    if key not in properties:
                        found.append(path + "." + jstr(key) + ": not one of " + jstr(list(properties)))
            for key, inner in properties.items():
                if key in value and isinstance(inner, dict):
                    self.value(value[key], inner, path + "." + key, found, False)


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def same(a, b):
    """Java's equals on JSON values: true is not 1, and 1 is not 1.0."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if is_number(a) or is_number(b):
        return is_number(a) and is_number(b) and type(a) is type(b) and a == b
    return a == b


def utf16(text):
    """A string's length as Java counts it."""
    return len(text.encode("utf-16-le")) // 2


def is_a(kind, value):
    if kind == "string":
        return isinstance(value, str)
    if kind == "number":
        return is_number(value)
    if kind == "integer":
        return isinstance(value, int) and not isinstance(value, bool) or isinstance(value, float) and value.is_integer()
    if kind == "boolean":
        return isinstance(value, bool)
    if kind == "array":
        return isinstance(value, list)
    if kind == "object":
        return isinstance(value, dict)
    return True


def article(kind):
    return {"array": "a list", "object": "an object", "integer": "a whole number"}.get(kind, "a " + kind)


def describe(value):
    if value is None:
        return "null"
    if isinstance(value, dict):
        return "an object"
    if isinstance(value, list):
        return "a list"
    if isinstance(value, str):
        return "a string"
    if isinstance(value, bool):
        return "true or false"
    if is_number(value):
        return "a number"
    return type(value).__name__


def check(messages, catalog):
    """What is wrong with messages (render_a2ui's) against catalog, one line each, and its charts' specs by id."""
    found = []
    charts = {}
    if not isinstance(messages, list) or len(messages) != 1 or not isinstance(messages[0], dict):
        found.append("messages: send one message, {\"version\": \"1.0\", \"createSurface\": {\"surfaceId\": ..., "
                     "\"catalogId\": \"" + jstr(catalog.id) + "\", \"components\": [...]}}")
        return found, charts
    message = messages[0]
    if message.get("version") != VERSION or not isinstance(message.get("version"), str):
        found.append("messages[0].version: must be \"" + VERSION + "\"")
    for key in message:
        if key not in ("version", "createSurface"):
            found.append("messages[0]." + jstr(key) + ": only createSurface, with its components in it")
    surface = message.get("createSurface")
    if not isinstance(surface, dict):
        found.append("messages[0].createSurface: needs the surface, its components in it")
        return found, charts
    at = "createSurface"
    surface_id = surface.get("surfaceId")
    if not isinstance(surface_id, str) or not SURFACE_ID.fullmatch(surface_id):
        found.append(at + ".surfaceId: a short name of letters, digits and dashes, e.g. dinner-tonight")
    if "catalogId" in surface and not same(catalog.id, surface["catalogId"]):
        found.append(at + ".catalogId: must be \"" + jstr(catalog.id) + "\"")
    for key in surface:
        if key not in ("surfaceId", "catalogId", "components"):
            found.append(at + "." + jstr(key) + ": not used here; values are literal, so there is no data model")
    components = surface.get("components")
    if not isinstance(components, list) or not components:
        found.append(at + ".components: needs the components, one with the id root")
        return found, charts
    if len(components) > MOST_COMPONENTS:
        found.append(at + ".components: " + str(len(components)) + " pieces, more than " + str(MOST_COMPONENTS)
                     + "; a reply this big is too much at once, show less")
    _bindings(components, at + ".components", found)

    by_id = {}
    for i, component in enumerate(components):
        path = at + ".components[" + str(i) + "]"
        if not isinstance(component, dict):
            found.append(path + ": must be an object")
            continue
        cid = component.get("id")
        if not isinstance(cid, str) or not cid.strip():
            found.append(path + ".id: needs an id")
            continue
        if cid in by_id:
            found.append(path + ".id: \"" + cid + "\" is used twice")
        else:
            by_id[cid] = component
        kind = component.get("component")
        if not isinstance(kind, str):
            found.append(path + ".component: say which piece it is, e.g. \"Text\"")
            continue
        catalog.check(kind, component, path + " (" + cid + ")", found)
        if kind == "VegaChart" and isinstance(component.get("spec"), dict):
            found.extend(path + " (" + cid + ")." + problem for problem in vega_rules.problems(component["spec"]))
            charts[cid] = component["spec"]
        if kind == "Image" and isinstance(component.get("url"), str) and not component["url"].startswith("https://"):
            found.append(path + " (" + cid + ").url: the photo's https address on the web, where you found it")
    _tree(by_id, found)
    return found, charts


def _bindings(value, path, found):
    """A data binding or function call anywhere: values are literal here."""
    if isinstance(value, dict):
        for key, inner in value.items():
            if key in ("@path", "@call", "@index"):
                found.append(path + "." + key + ": values are literal here; write the value itself")
            elif key != "spec":
                _bindings(inner, path + "." + jstr(key), found)
    elif isinstance(value, list):
        for i, inner in enumerate(value):
            _bindings(inner, path + "[" + str(i) + "]", found)


def _tree(by_id, found):
    """One tree from root: children that exist, no cycle, nothing left out, not too deep, buttons labelled by a Text."""
    if "root" not in by_id:
        found.append("components: one needs the id root: the piece the surface starts from")
        return
    seen = set()
    buttons = [0]
    _walk("root", by_id, seen, [], buttons, found)
    for cid in by_id:
        if cid not in seen:
            found.append("components (" + cid + "): no piece has it as a child, so it is never drawn")
    if buttons[0] > MOST_BUTTONS:
        found.append("components: " + str(buttons[0]) + " buttons, more than " + str(MOST_BUTTONS)
                     + "; offer the few that matter")


def _walk(cid, by_id, seen, path, buttons, found):
    component = by_id[cid]
    if cid in path:
        found.append("components (" + cid + "): is its own ancestor (" + " > ".join(path) + " > " + cid + ")")
        return
    if cid in seen:
        found.append("components (" + cid + "): is a child of two pieces; give each its own")
        return
    seen.add(cid)
    if len(path) >= DEEPEST:
        found.append("components (" + cid + "): " + str(len(path) + 1) + " levels deep, more than " + str(DEEPEST)
                     + "; lay it out flatter")
    path.append(cid)
    if component.get("component") == "Button":
        buttons[0] += 1
        child = component.get("child")
        label = by_id.get(child) if isinstance(child, str) else None
        if label is not None and label.get("component") != "Text":
            found.append("components (" + cid + ").child: a Button's label is a Text")
    for child in _children(component):
        if child not in by_id:
            found.append("components (" + cid + "): child \"" + child + "\" isn't a component of the surface")
        else:
            _walk(child, by_id, seen, path, buttons, found)
    path.pop()


def _children(component):
    children = []
    if isinstance(component.get("child"), str):
        children.append(component["child"])
    if isinstance(component.get("children"), list):
        children.extend(child for child in component["children"] if isinstance(child, str))
    return children


def unwrap(value):
    """The messages: render_a2ui's arguments, an example or a layout ({"messages": [...]}), a list, or one message."""
    if isinstance(value, dict) and "messages" in value:
        return value["messages"]
    if isinstance(value, dict) and "createSurface" in value:
        return [value]
    return value


def main(argv):
    if len(argv) != 2:
        print("usage: validate.py <surface.json | ->", file=sys.stderr)
        return 1
    try:
        text = sys.stdin.read() if argv[1] == "-" else Path(argv[1]).read_text(encoding="utf-8")
        messages = unwrap(json.loads(text))
    except (OSError, ValueError) as unreadable:
        print(argv[1] + ": can't read it as JSON: " + str(unreadable))
        return 1
    found, _ = check(messages, Catalog.read())
    if found:
        print("\n".join(found))
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
