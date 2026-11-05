"""Run validate.py over the layouts and, in the library, over render_a2ui's examples: good ones and layouts must print ok,
each bad one must fail with a line holding its expect. Also checks that SKILL.md's list of pieces is what pieces.py makes
from catalog.json, and, in the library, that catalog.json is the tool's (../../client-tools/render_a2ui/catalog.json).
Installed alone (no library around it), it
says so and checks what the skill holds.

    python3 check_examples.py [--source <traceflow repo>]

With --source, also checks that the tool's catalog and examples are the same as traceflow's own.
Prints a line per check and exits 1 when any fails.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
SKILL = Path(__file__).resolve().parent.parent
TOOL = SKILL.parent.parent / "client-tools" / "render_a2ui"
"""The tool's folder in the library; absent where the skill is installed alone."""
sys.path.insert(0, str(SKILL / "scripts"))

import pieces  # noqa: E402  (beside this script)

TOOLS = "backend/traceflow-parent/traceflow-effects/traceflow-tools/src"
START, END = "<!-- pieces: made by scripts/pieces.py -->", "<!-- /pieces -->"


def run(path):
    """validate.py's exit code and output for path."""
    done = subprocess.run([sys.executable, str(SKILL / "scripts" / "validate.py"), str(path)],
                          capture_output=True, text=True)
    return done.returncode, done.stdout.strip()


def name(path):
    """path from the skill, or from the library's client-tools/ for the tool's examples."""
    return str(path.relative_to(SKILL if path.is_relative_to(SKILL) else TOOL.parent))


def report(passed, line):
    print(("PASS " if passed else "FAIL ") + line)
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="a checkout of the traceflow repo, to compare the copied files with")
    args = parser.parse_args()
    failed = 0
    in_library = TOOL.is_dir()
    if not in_library:
        print("NOTE no library around this skill (" + str(TOOL) + "): checking only what the skill holds")
    examples = TOOL / "examples"
    good = sorted((examples / "good").glob("*.json")) + sorted((SKILL / "layouts").glob("*.json"))
    for path in good:
        code, out = run(path)
        failed += report(code == 0 and out == "ok", name(path) + ": " + out.splitlines()[0][:110])
    for path in sorted((examples / "bad").glob("*.json")):
        code, out = run(path)
        expect = json.loads(path.read_text(encoding="utf-8"))["expect"]
        said = next((line for line in out.splitlines() if expect in line), out.splitlines()[0] if out else "nothing")
        failed += report(code == 1 and any(expect in line for line in out.splitlines()),
                         name(path) + ": expected \"" + expect + "\", got: " + said[:140])

    body = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    listed = body.split(START, 1)[1].split(END, 1)[0].strip() if START in body and END in body else None
    made = pieces.markdown(json.loads((SKILL / "catalog.json").read_text(encoding="utf-8")))
    failed += report(listed == made, "SKILL.md's pieces are catalog.json's"
                     + ("" if listed == made else ": run scripts/pieces.py and paste its output between the markers"))
    if in_library:
        same = (TOOL / "catalog.json").read_bytes() == (SKILL / "catalog.json").read_bytes()
        failed += report(same, "catalog.json is client-tools/render_a2ui/catalog.json"
                         + ("" if same else ": copy the tool's catalog.json over the skill's"))

    if args.source:
        tools = Path(args.source) / TOOLS
        pairs = [(tools / "main/resources/a2ui/catalog.json", TOOL / "catalog.json")]
        pairs += [(theirs, examples / theirs.parent.name / theirs.name)
                  for theirs in sorted((tools / "test/resources/generative/a2ui").glob("*/*.json"))]
        for theirs, ours in pairs:
            same = ours.exists() and ours.read_bytes() == theirs.read_bytes()
            failed += report(same, "copy of traceflow's " + str(theirs.relative_to(tools))
                             + ("" if same else (": differs" if ours.exists() else ": missing")))
    print("all passed" if not failed else str(failed) + " failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
