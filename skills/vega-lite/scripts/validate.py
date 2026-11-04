"""Check a Vega-Lite spec the way render_vega will, before sending it.

    python3 validate.py chart.json     (or - to read it from stdin)

The file is the spec itself, render_vega's arguments ({"title": ..., "spec": {...}}), or one of render_vega's examples.
Runs traceflow's chart rules (vega_rules.py, beside this script), then, when vl-convert-python is installed, compiles the
spec with vl_convert.vegalite_to_vega to prove it renders. Prints "ok" and whether it compiled, or one problem per line.
Exits 0 when the spec is fine, 1 when it isn't.
"""

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import vega_rules  # noqa: E402  (beside this script)

WRAPPER = {"spec", "title", "why", "expect", "asked", "said"}
"""The keys of render_vega's arguments and of an example; a spec with any other key is a spec, not a wrapper."""


def read(name):
    """The JSON in file name, or on stdin for -."""
    text = sys.stdin.read() if name == "-" else Path(name).read_text(encoding="utf-8")
    return json.loads(text)


def unwrap(value):
    """The spec: inside render_vega's arguments or an example, else the value itself."""
    if isinstance(value, dict) and "spec" in value and set(value) <= WRAPPER:
        return value["spec"]
    return value


def why(failed):
    """What vl-convert said went wrong, in one line: its message, not its JavaScript stack."""
    lines = [line.strip() for line in str(failed).splitlines() if line.strip() and not line.strip().startswith("at ")]
    if len(lines) > 1 and lines[0].endswith(":"):
        lines = lines[1:]
    return lines[0] if lines else type(failed).__name__


def compiled(spec):
    """None when the spec compiles (or can't be tried here), else why it doesn't; and a note saying which."""
    try:
        import vl_convert
    except ImportError:
        return None, "not compiled: vl-convert-python isn't installed here"
    try:
        vl_convert.vegalite_to_vega(spec)
    except Exception as failed:  # vl_convert raises ValueError, but say whatever it says
        return ("spec: Vega-Lite can't compile it (" + why(failed) + "); check the mark's name and each encoding's "
                "type (quantitative, nominal, ordinal, temporal)"), None
    return None, "compiled with vl-convert " + getattr(vl_convert, "__version__", "")


def check(spec):
    """The problems with spec, and a note on compiling when there are none."""
    found = vega_rules.problems(spec)
    if found:
        return found, None
    problem, note = compiled(spec)
    return ([problem] if problem else []), note


def main(argv):
    if len(argv) != 2:
        print("usage: validate.py <spec.json | ->", file=sys.stderr)
        return 1
    try:
        spec = unwrap(read(argv[1]))
    except (OSError, ValueError) as unreadable:
        print(argv[1] + ": can't read it as JSON: " + str(unreadable))
        return 1
    found, note = check(spec)
    if found:
        print("\n".join(found))
        return 1
    print("ok (" + note + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
