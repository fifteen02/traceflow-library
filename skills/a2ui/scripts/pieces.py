"""Print the catalog's pieces as the Markdown list SKILL.md carries, so the two stay in step.

    python3 pieces.py

Reads catalog.json from the skill's folder: one line per piece, its use (the catalog's description) and its properties,
required ones in bold, with their choices and limits. check_examples.py fails when SKILL.md's list differs from this.
"""

import json
import sys
from pathlib import Path

CATALOG = Path(__file__).resolve().parent.parent / "catalog.json"


def limits(schema):
    """A list's size limits: 1–8, or ≤30 when it has only a most."""
    least, most = schema.get("minItems"), schema.get("maxItems")
    if least is not None and most is not None:
        return str(least) + "–" + str(most)
    return "≤" + str(most) if most is not None else ("≥" + str(least) if least is not None else "")


def shape(schema, defs):
    """A property's choices and limits in a few words."""
    ref = schema.get("$ref")
    if isinstance(ref, str):
        name = ref[ref.rfind("/") + 1:]
        target = defs.get(name, {})
        if name == "Child":
            return "an id"
        if name == "Children":
            return "ids, " + limits(target)
        if name == "Weight":
            return "a number, its share of a Row"
        if name == "Action":
            return "{event: {**name**, **userMessage** ≤" + str(target["properties"]["event"]["properties"]["userMessage"]["maxLength"]) + "}}"
        fields = target.get("properties", {})
        required = set(target.get("required", []))
        return "{" + ", ".join("**" + key + "**" if key in required else key for key in fields) + "}"
    if "enum" in schema:
        return " | ".join(schema["enum"])
    kind = schema.get("type", "")
    if kind == "array":
        items = shape(schema.get("items", {}), defs)
        return "list of " + ("objects" if items == "object" else items) + (", " + limits(schema) if limits(schema) else "")
    words = kind
    if "maxLength" in schema:
        words += " ≤" + str(schema["maxLength"])
    if "minimum" in schema and "maximum" in schema:
        words += " " + str(schema["minimum"]) + "–" + str(schema["maximum"])
    return words


def markdown(catalog):
    defs = catalog.get("$defs", {})
    lines = []
    for name, piece in catalog["components"].items():
        required = set(piece.get("required", []))
        props = [("**" + key + "**" if key in required else key) + " (" + shape(schema, defs) + ")"
                 for key, schema in piece.get("properties", {}).items() if key != "component"]
        lines.append("- `" + name + "`: " + piece.get("description", "") + " " + "; ".join(props) + ".")
    return "\n".join(lines)


if __name__ == "__main__":
    print(markdown(json.loads(CATALOG.read_text(encoding="utf-8"))))
    sys.exit(0)
