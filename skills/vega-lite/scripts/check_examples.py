"""Run validate.py over every example of render_vega in the library (../../client-tools/render_vega/examples): each good
one must print ok, each bad one must fail with a line holding its expect. Installed alone (no library around it), it says
so and has nothing to run.

    python3 check_examples.py [--source <traceflow repo>]

With --source, also checks that the tool's examples (and vega_rules.py's rules, through them) are the same as
traceflow's own, under backend/.../traceflow-tools/src/test/resources/generative/vega. Prints a line per example and
exits 1 when any fails.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
EXAMPLES = SKILL.parent.parent / "client-tools" / "render_vega" / "examples"
"""The tool's examples in the library; absent where the skill is installed alone."""
TRACEFLOW_EXAMPLES = "backend/traceflow-parent/traceflow-effects/traceflow-tools/src/test/resources/generative/vega"


def run(path):
    """validate.py's exit code and output for path."""
    done = subprocess.run([sys.executable, str(SKILL / "scripts" / "validate.py"), str(path)],
                          capture_output=True, text=True)
    return done.returncode, done.stdout.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="a checkout of the traceflow repo, to compare the copied examples with")
    args = parser.parse_args()
    failed = 0
    if not EXAMPLES.is_dir():
        print("NOTE no library around this skill (" + str(EXAMPLES) + "): no examples to run")
    for kind in ("good", "bad"):
        for path in sorted((EXAMPLES / kind).glob("*.json")):
            code, out = run(path)
            name = kind + "/" + path.name
            if kind == "good":
                passed = code == 0 and out.startswith("ok")
                print(("PASS " if passed else "FAIL ") + name + ": " + out.splitlines()[0][:110])
            else:
                expect = json.loads(path.read_text(encoding="utf-8"))["expect"]
                passed = code == 1 and any(expect in line for line in out.splitlines())
                said = next((line for line in out.splitlines() if expect in line), out.splitlines()[0] if out else "nothing")
                print(("PASS " if passed else "FAIL ") + name + ": expected \"" + expect + "\", got: " + said[:140])
            failed += not passed
    if args.source:
        source = Path(args.source) / TRACEFLOW_EXAMPLES
        for theirs in sorted(source.glob("*/*.json")):
            ours = EXAMPLES / theirs.parent.name / theirs.name
            same = ours.exists() and ours.read_bytes() == theirs.read_bytes()
            print(("PASS " if same else "FAIL ") + "copy of traceflow's " + theirs.parent.name + "/" + theirs.name
                  + ("" if same else (": differs" if ours.exists() else ": missing")))
            failed += not same
    print(("all passed" if not failed else str(failed) + " failed"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
