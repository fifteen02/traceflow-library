"""A surface written with a data model, as the literal surface it stands for (A2UI 1.0's read-only data binding).

A copy, in Python, of traceflow's A2uiData (the source of truth, beside A2uiSurfaces in the traceflow repo), with the
same rules and wording: the surface's dataModel read where a value is {"@path": "/place/name"} (a JSON Pointer;
relative inside a template), a function run where it is {"@call": "formatCurrency", "args": {...}}, and a
children {"path": "/places", "componentId": "place"} template drawn once per item, each copy's id the template's with
its place in the list (place#0, place#1). Strings in formatString say ${/path}, ${relative} or
${formatDate(value: ${/day}, format: 'EEEE')}. Nothing writes the data, so expanding once gives everything the surface
shows, and validate.py checks what is drawn. Standard library only.
"""

import re
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation

MOST_EXPANDED = 200
"""The most pieces expanding may make, so a template over a long list stops rather than runs on."""
FUNCTIONS = ("formatCurrency", "formatDate", "formatNumber", "formatString", "join", "pluralize")
"""The functions an agent may call."""

_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
           "November", "December"]
_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_SYMBOLS = {"EUR": "€", "GBP": "£", "USD": "US$"}


def binds(value):
    """Whether value binds, calls or templates anywhere, so it needs expanding before it can be drawn; a string that says
    ${…} counts, so expanding can say it is only filled in by formatString."""
    if isinstance(value, str):
        return _fills_in(value)
    if isinstance(value, dict):
        if "@path" in value or "@call" in value or isinstance(value.get("children"), dict):
            return True
        return any(binds(inner) for key, inner in value.items() if key != "spec")
    return isinstance(value, list) and any(binds(item) for item in value)


def _fills_in(text):
    """Whether text says ${…} unescaped, which only formatString fills in."""
    at = text.find("${")
    while at >= 0:
        if at == 0 or text[at - 1] != "\\":
            return True
        at = text.find("${", at + 2)
    return False


def expand(components, data_model):
    """components with data_model read into them: (the components as drawn, the problems)."""
    return _Expanding(data_model).run(components)


class _Wrong(Exception):
    pass


class _Expanding:
    def __init__(self, data):
        self.data = data if isinstance(data, dict) else {}
        self.by_id = {}
        self.out = []
        self.problems = []

    def run(self, components):
        for component in components:
            if isinstance(component, dict) and isinstance(component.get("id"), str):
                self.by_id.setdefault(component["id"], component)
        in_templates = set()
        for component in self.by_id.values():
            template = component.get("children")
            if isinstance(template, dict) and isinstance(template.get("componentId"), str):
                self._under(template["componentId"], in_templates)
        for component in components:
            if not isinstance(component, dict) or not isinstance(component.get("id"), str):
                self.out.append(component)
            elif component["id"] not in in_templates:
                self._emit(component, "", "", frozenset())
        return self.out, self.problems

    def _under(self, cid, found):
        if cid in found or not isinstance(self.by_id.get(cid), dict):
            found.add(cid)
            return
        found.add(cid)
        component = self.by_id[cid]
        if isinstance(component.get("child"), str):
            self._under(component["child"], found)
        if isinstance(component.get("children"), list):
            for child in component["children"]:
                if isinstance(child, str):
                    self._under(child, found)
        template = component.get("children")
        if isinstance(template, dict) and isinstance(template.get("componentId"), str):
            self._under(template["componentId"], found)

    def _emit(self, component, scope, suffix, drawing):
        if len(self.out) >= MOST_EXPANDED:
            if len(self.out) == MOST_EXPANDED:
                self.problems.append("components: the templates make more than " + str(MOST_EXPANDED)
                                     + " pieces; show fewer items")
            self.out.append({})
            return
        cid = component["id"]
        at = "components (" + cid + ")"
        drawn = {}
        for key, value in component.items():
            if key == "id":
                drawn["id"] = cid + suffix
            elif key == "child":
                drawn["child"] = value + suffix if isinstance(value, str) else value
            elif key == "children":
                drawn["children"] = self._children(value, scope, suffix, drawing, at)
            elif key == "spec":
                drawn["spec"] = value
            else:
                drawn[key] = self._resolve(value, scope, at + "." + key)
        self.out.append(drawn)
        if suffix and isinstance(component.get("child"), str):
            self._inside(component["child"], scope, suffix, drawing)
        if suffix and isinstance(component.get("children"), list):
            for child in component["children"]:
                if isinstance(child, str):
                    self._inside(child, scope, suffix, drawing)

    def _inside(self, cid, scope, suffix, drawing):
        if cid in drawing or not isinstance(self.by_id.get(cid), dict):
            return
        self._emit(self.by_id[cid], scope, suffix, drawing | {cid})

    def _children(self, value, scope, suffix, drawing, at):
        if isinstance(value, list):
            return [child + suffix if isinstance(child, str) else child for child in value]
        if not isinstance(value, dict):
            return value
        path, repeated = value.get("path"), value.get("componentId")
        if not isinstance(path, str) or not isinstance(repeated, str):
            self.problems.append(at + ".children: a template is {\"path\": \"/items\", \"componentId\": \"item\"}")
            return []
        if repeated not in self.by_id:
            self.problems.append(at + ".children.componentId: \"" + repeated + "\" isn't a component of the surface")
            return []
        list_path = _pointer(path, scope)
        items = self._read(list_path)
        if not isinstance(items, list):
            self.problems.append(at + ".children.path: " + list_path + " isn't a list in the dataModel")
            return []
        if repeated in drawing:
            self.problems.append(at + ".children: \"" + repeated + "\" draws itself")
            return []
        ids = []
        for i in range(len(items)):
            ids.append(repeated + suffix + "#" + str(i))
            self._emit(self.by_id[repeated], list_path + "/" + str(i), suffix + "#" + str(i), drawing | {repeated})
        return ids

    def _resolve(self, value, scope, at):
        if isinstance(value, dict):
            if "@path" in value:
                if len(value) != 1 or not isinstance(value["@path"], str):
                    self.problems.append(at + ": a binding is {\"@path\": \"/a/b\"} on its own")
                    return None
                pointer = _pointer(value["@path"], scope)
                found = self._read(pointer)
                if found is None:
                    self.problems.append(at + ": " + pointer + " isn't in the dataModel")
                return found
            if "@call" in value:
                return self._call(value, scope, at)
            resolved = {}
            for key, inner in value.items():
                if key.startswith("@@"):
                    resolved[key[1:]] = self._resolve(inner, scope, at + "." + key)
                elif key.startswith("@"):
                    self.problems.append(at + "." + key + ": keys starting with @ are A2UI's; write @@ for a literal @")
                else:
                    resolved[key] = self._resolve(inner, scope, at + "." + key)
            return resolved
        if isinstance(value, list):
            return [self._resolve(item, scope, at + "[" + str(i) + "]") for i, item in enumerate(value)]
        if isinstance(value, str) and _fills_in(value):
            self.problems.append(at + ": \"" + value + "\" is drawn as written; ${…} is only filled in by formatString: "
                                 + "{\"@call\": \"formatString\", \"args\": {\"value\": \"" + value + "\"}} (\\${ for a literal ${)")
        return value

    def _call(self, call, scope, at):
        name = str(call.get("@call"))
        if name not in FUNCTIONS:
            self.problems.append(at + ": \"" + name + "\" isn't a function here; use one of " + ", ".join(FUNCTIONS))
            return None
        args = {}
        if isinstance(call.get("args"), dict):
            for key, value in call["args"].items():
                # formatString's own template is its to fill in, not a string drawn as written
                own = name == "formatString" and key == "value" and isinstance(value, str)
                args[key] = value if own else self._resolve(value, scope, at + ".args." + key)
        return self._run(name, args, scope, at)

    def _run(self, name, args, scope, at):
        try:
            if name == "formatString":
                return self._interpolate(_text(args.get("value")), scope, at)
            if name == "formatNumber":
                return _number(args, None)
            if name == "formatCurrency":
                return _number(args, _text(args.get("currency", "EUR")))
            if name == "formatDate":
                return _date(args.get("value"), _text(args.get("format")))
            if name == "pluralize":
                count = float(_decimal(args.get("value")))
                chosen = args.get("zero") if count == 0 and "zero" in args else args.get("one") if count == 1 else args.get("other")
                return _text(args.get("other") if chosen is None else chosen)
            if name == "join":
                values = args.get("values")
                if isinstance(values, list):
                    return (_text(args["separator"]) if "separator" in args else ", ").join(_text(v) for v in values)
                return _text(values)
        except _Wrong as wrong:
            self.problems.append(at + ": " + name + " " + str(wrong))
        return None

    # formatString's ${…}: a path, or a function with named arguments of literals and nested ${…}

    def _interpolate(self, template, scope, at):
        out = []
        i = 0
        while i < len(template):
            if template.startswith("\\${", i):
                out.append("${")
                i += 3
                continue
            if template.startswith("${", i):
                end = _closing(template, i + 1)
                if end < 0:
                    self.problems.append(at + ": a ${ without its }")
                    return "".join(out)
                out.append(_text(self._expression(template[i + 2:end], scope, at)))
                i = end + 1
                continue
            out.append(template[i])
            i += 1
        return "".join(out)

    def _expression(self, source, scope, at):
        trimmed = source.strip()
        open_at = trimmed.find("(")
        if open_at > 0 and trimmed.endswith(")") and re.fullmatch(r"[A-Za-z_]\w*", trimmed[:open_at]):
            name = trimmed[:open_at]
            if name not in FUNCTIONS:
                self.problems.append(at + ": \"" + name + "\" isn't a function here")
                return ""
            args = {}
            for part in _split(trimmed[open_at + 1:-1]):
                colon = part.find(":")
                if colon > 0:
                    args[part[:colon].strip()] = self._literal(part[colon + 1:], scope, at)
            result = self._run(name, args, scope, at)
            return "" if result is None else result
        pointer = _pointer(trimmed, scope)
        found = self._read(pointer)
        if found is None:
            self.problems.append(at + ": ${" + trimmed + "}: " + pointer + " isn't in the dataModel")
            return ""
        return found

    def _literal(self, raw, scope, at):
        value = raw.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            return re.sub(r"\\(['\"\\])", r"\1", value[1:-1])
        if re.fullmatch(r"-?\d+(\.\d+)?", value):
            return Decimal(value)
        if value in ("true", "false"):
            return value == "true"
        if value.startswith("${") and _closing(value, 1) == len(value) - 1:
            return self._expression(value[2:-1], scope, at)
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1]
            return [] if not inner.strip() else [self._literal(item, scope, at) for item in _split(inner)]
        return value

    def _read(self, pointer):
        node = self.data
        if pointer in ("/", ""):
            return node
        for raw in pointer[1:].split("/"):
            key = raw.replace("~1", "/").replace("~0", "~")
            if isinstance(node, dict):
                node = node.get(key)
            elif isinstance(node, list) and key.isdigit() and int(key) < len(node):
                node = node[int(key)]
            else:
                return None
        return node


def _pointer(path, scope):
    return path if path.startswith("/") else scope + "/" + path


def _split(source):
    """source split at top-level commas: not inside quotes, brackets or ${…}."""
    parts, depth, start, quote, i = [], 0, 0, None, 0
    while i < len(source):
        c = source[i]
        if quote:
            if c == "\\":
                i += 1
            elif c == quote:
                quote = None
        elif c in "'\"":
            quote = c
        elif c in "{[(":
            depth += 1
        elif c in "}])":
            depth -= 1
        elif c == "," and depth == 0:
            parts.append(source[start:i])
            start = i + 1
        i += 1
    parts.append(source[start:])
    return parts


def _closing(source, open_at):
    """Where the } that closes the { at open_at is; -1 when none does."""
    depth, quote, i = 0, None, open_at
    while i < len(source):
        c = source[i]
        if quote:
            if c == "\\":
                i += 1
            elif c == quote:
                quote = None
        elif c in "'\"":
            quote = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _decimal(value):
    if isinstance(value, bool):
        raise _Wrong("needs a number, not \"" + _text(value) + "\"")
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    try:
        return Decimal(_text(value).strip())
    except InvalidOperation:
        raise _Wrong("needs a number, not \"" + _text(value) + "\"") from None


def _number(args, currency):
    """As Java's en-GB number and en-IE currency formats write it: 1,240.5 and €1,065.00."""
    amount = _decimal(args.get("value"))
    decimals = args.get("decimals")
    if isinstance(decimals, (int, float, Decimal)) and not isinstance(decimals, bool):
        places = int(decimals)
        shown = f"{amount:,.{places}f}" if args.get("grouping") is not False else f"{amount:.{places}f}"
    elif currency is not None:
        shown = f"{amount:,.2f}" if args.get("grouping") is not False else f"{amount:.2f}"
    else:
        rounded = amount.quantize(Decimal("0.001")).normalize()
        shown = f"{rounded:,f}" if args.get("grouping") is not False else f"{rounded:f}"
    if currency is None:
        return shown
    negative = shown.startswith("-")
    return ("-" if negative else "") + _SYMBOLS.get(currency, currency) + shown.lstrip("-")


def _date(value, pattern):
    """A date, time or both as the pattern says, in the Unicode pattern letters Java's DateTimeFormatter reads."""
    text = _text(value).strip()
    try:
        if re.fullmatch(r"\d{1,2}:\d{2}", text):
            when = time.fromisoformat(text.zfill(5))
        elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            when = date.fromisoformat(text)
        else:
            when = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        raise _Wrong("can't read \"" + text + "\" as a date or time") from None
    pattern = pattern or "d MMMM yyyy"

    def part(token):
        letter, n = token[0], len(token)
        if letter == "y":
            return str(when.year) if n != 2 else str(when.year)[-2:]
        if letter == "M":
            return _MONTHS[when.month - 1] if n >= 4 else _MONTHS[when.month - 1][:3] if n == 3 else str(when.month).zfill(n)
        if letter == "d":
            return str(when.day).zfill(n)
        if letter == "E":
            name = _DAYS[when.weekday()]
            return name if n >= 4 else name[:3]
        if letter == "H":
            return str(when.hour).zfill(n)
        if letter == "h":
            return str(when.hour % 12 or 12).zfill(n)
        if letter == "m":
            return str(when.minute).zfill(n)
        if letter == "a":
            return "am" if when.hour < 12 else "pm"
        return token

    out, i = [], 0
    while i < len(pattern):
        c = pattern[i]
        if c == "'":
            end = pattern.find("'", i + 1)
            end = len(pattern) if end < 0 else end
            out.append(pattern[i + 1:end] or "'")
            i = end + 1
        elif c.isalpha():
            j = i
            while j < len(pattern) and pattern[j] == c:
                j += 1
            try:
                out.append(part(pattern[i:j]))
            except AttributeError:
                raise _Wrong("format \"" + pattern + "\" asks for what \"" + text + "\" hasn't") from None
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _text(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, Decimal):
        normal = value.normalize()
        return format(normal, "f")
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)
