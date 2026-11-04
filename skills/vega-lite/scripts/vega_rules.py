"""What a Vega-Lite spec sent to render_vega (or drawn by an A2UI VegaChart) must be, before it is compiled.

A copy, in Python, of traceflow's VegaLiteRules (the source of truth, in the traceflow repo:
backend/traceflow-parent/traceflow-effects/traceflow-tools/src/main/java/com/fifteen02/traceflow/tool/generative/VegaLiteRules.java).
Same rules, same limits, same wording: its data inline (no url or href anywhere but in the rows themselves), at most
MOST_ROWS rows, every field its encodings name in its rows, at most MOST_COLOURS colours, a pie of at most MOST_SLICES
slices and one y axis. Each problem is one line: where, what is wrong and what to do instead.

The vega-lite and a2ui skills each ship this same file, since skills install separately; keep the two identical.
Standard library only.
"""

import json
import re

MOST_ROWS = 5000
"""The most rows a chart carries."""
MOST_COLOURS = 8
"""The most colours (values of a nominal colour field) a chart tells apart."""
MOST_SLICES = 6
"""The most slices a pie or donut has."""

VIEWS = ["layer", "concat", "hconcat", "vconcat"]
"""The keys that make a chart of several views; each holds specs of its own."""
CHANNELS = ["x", "y", "x2", "y2", "color", "theta", "radius", "size", "shape", "opacity", "text", "row", "column",
            "facet", "detail", "xOffset", "yOffset"]
"""Encoding channels whose field must be in the rows."""


def jstr(value):
    """A value as Java's String.valueOf writes it, so messages read as traceflow's do."""
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, list):
        return "[" + ", ".join(jstr(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(jstr(k) + "=" + jstr(v) for k, v in value.items()) + "}"
    return str(value)


def problems(spec):
    """What is wrong with spec: empty when nothing is."""
    found = []
    if not isinstance(spec, dict) or not spec:
        found.append("spec: give the Vega-Lite spec as an object, e.g. "
                     "{\"data\": {\"values\": [...]}, \"mark\": \"bar\", \"encoding\": {...}}")
        return found
    _addresses(spec, "spec", found)
    _view(spec, None, "spec", found)
    resolve = spec.get("resolve")
    if isinstance(resolve, dict) and isinstance(resolve.get("scale"), dict) and resolve["scale"].get("y") == "independent":
        found.append("spec.resolve.scale.y: two y axes read as one; draw two charts side by side (hconcat) or index both to 100")
    return found


def _addresses(value, path, found):
    """A url or href anywhere but inside rows (values, datasets): the app fetches nothing."""
    if isinstance(value, dict):
        for key, inner in value.items():
            at = path + "." + jstr(key)
            if key in ("url", "href"):
                found.append(at + ": a chart reads nothing from an address; put the rows in data.values")
            elif key not in ("values", "datasets"):
                _addresses(inner, at, found)
    elif isinstance(value, list):
        for i, inner in enumerate(value):
            _addresses(inner, path + "[" + str(i) + "]", found)


def _view(spec, inherited, path, found):
    """One view: its own data or inherited, its rows' count and fields, its encodings, then its own views."""
    rows = inherited
    data = spec.get("data")
    if isinstance(data, dict):
        values = data.get("values")
        if isinstance(values, list):
            rows = values
            if len(values) > MOST_ROWS:
                found.append(path + ".data.values: " + str(len(values)) + " rows, more than " + str(MOST_ROWS)
                             + "; sum or average them into fewer before charting")
        elif "url" not in data and "name" not in data:
            found.append(path + ".data: give the rows inline as data.values")
    views = any(key in spec for key in VIEWS) or "spec" in spec
    if not views and rows is None and "datasets" not in spec:
        found.append(path + ": no data; give the rows inline as data.values")
    if "mark" in spec or "encoding" in spec:
        _encodings(spec, rows, path, found)
    for key in VIEWS:
        inner = spec.get(key)
        if isinstance(inner, list):
            for i, one in enumerate(inner):
                if isinstance(one, dict):
                    _view(one, rows, path + "." + key + "[" + str(i) + "]", found)
    if isinstance(spec.get("spec"), dict):
        _view(spec["spec"], rows, path + ".spec", found)


def _encodings(spec, rows, path, found):
    if "mark" not in spec:
        found.append(path + ": no mark; say what draws the data, e.g. \"mark\": \"bar\"")
    fields = _fields(rows)
    derived = _derived(spec)
    encoding = spec.get("encoding")
    if not isinstance(encoding, dict):
        return
    for channel in CHANNELS:
        definition = encoding.get(channel)
        if not isinstance(definition, dict) or not isinstance(definition.get("field"), str):
            continue
        field = definition["field"]
        root = re.split(r"[.\[]", field, maxsplit=1)[0]
        if fields and root not in fields and root not in derived:
            found.append(path + ".encoding." + channel + ".field: \"" + field + "\" isn't in the rows (they have "
                         + ", ".join(fields) + ")")
    color = encoding.get("color")
    if isinstance(color, dict) and isinstance(color.get("field"), str) and color.get("type") == "nominal":
        distinct = _distinct(rows, color["field"])
        if distinct > MOST_COLOURS:
            found.append(path + ".encoding.color: " + str(distinct) + " colours, more than " + str(MOST_COLOURS)
                         + " can be told apart; keep the largest and group the rest as Other, or use a bar chart")
    if _is_arc(spec.get("mark")) and isinstance(color, dict) and isinstance(color.get("field"), str):
        slices = _distinct(rows, color["field"])
        if slices > MOST_SLICES:
            found.append(path + ".mark: a pie of " + str(slices) + " slices can't be read; use a bar chart, sorted, or "
                         + "keep " + str(MOST_SLICES - 1) + " and group the rest as Other")


def _is_arc(mark):
    return mark == "arc" or isinstance(mark, dict) and mark.get("type") == "arc"


def _fields(rows):
    """The fields its rows have, in the order first seen; empty when it has none to read."""
    fields = {}
    for row in rows or []:
        if isinstance(row, dict):
            for key in row:
                fields[jstr(key)] = True
    return list(fields)


def _derived(spec):
    """The fields its transforms make (as), which its encodings may name too."""
    made = set()
    transforms = spec.get("transform")
    if isinstance(transforms, list):
        for transform in transforms:
            _collect_as(transform, made)
    return made


def _collect_as(value, made):
    if isinstance(value, dict):
        for key, inner in value.items():
            if key == "as" and isinstance(inner, str):
                made.add(inner)
            elif key == "as" and isinstance(inner, list):
                made.update(jstr(name) for name in inner)
            else:
                _collect_as(inner, made)
    elif isinstance(value, list):
        for inner in value:
            _collect_as(inner, made)


def _distinct(rows, field):
    if rows is None:
        return 0
    values = set()
    for row in rows:
        if isinstance(row, dict) and field in row:
            # Typed, so 1, 1.0 and true stay three values, as they are in Java.
            value = row[field]
            values.add((type(value).__name__, json.dumps(value, sort_keys=True)))
    return len(values)
