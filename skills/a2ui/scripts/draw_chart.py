"""Draw a Vega-Lite spec as a PNG, to look at it before sending it or to put it in a report or a deck.

    python3 draw_chart.py chart.json charts/spending.png [--scale 2]

Checks the spec first, as validate_chart.py does, and draws nothing when it has a problem. The spec reads no address: its
rows must be inline. It draws as traceflow draws render_vega's PNG for WhatsApp and the other channels: the same look
and, unless the spec says its own size or has several views, 560 by 260 (a copy of DRAW and LOOK in ClientCallChecks.java,
traceflow repo, backend/traceflow-parent/traceflow-effects/traceflow-llm/src/main/java/com/fifteen02/traceflow/llm/agent/). Prints the PNG's path and size, or one problem per line. Exits 0 when it drew, 1 when it didn't.
"""

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_chart as validate  # noqa: E402  (beside this script)
import vl_convert  # noqa: E402

LOOK = {"font": "Helvetica", "background": "#ffffff", "padding": 12,
        "view": {"stroke": None}, "mark": {"color": "#3c5473"},
        "range": {"category": ["#3c5473", "#a0783e", "#1b7d82", "#704e7f", "#526629"]},
        "bar": {"cornerRadiusEnd": 4}, "line": {"strokeWidth": 2.5, "interpolate": "monotone"},
        "axis": {"domain": False, "ticks": False, "labelColor": "#7a736c", "titleColor": "#7a736c",
                 "gridColor": "#ebe7e3", "labelFontSize": 12, "titleFontWeight": "normal"}, "axisX": {"grid": False},
        "legend": {"orient": "top", "symbolType": "circle", "labelColor": "#57524d", "title": None},
        "title": {"anchor": "start", "fontSize": 15, "color": "#1c1a18"}}
"""The look traceflow draws charts with."""
SEVERAL = ("hconcat", "vconcat", "concat", "facet", "repeat")


def main():
    parser = argparse.ArgumentParser(description="Draw a Vega-Lite spec as a PNG.")
    parser.add_argument("spec", help="the spec's JSON file, render_vega's arguments, or - for stdin")
    parser.add_argument("out", help="the PNG to write, e.g. charts/spending.png")
    parser.add_argument("--scale", type=float, default=2.0, help="pixels per point (default 2, sharp on a phone)")
    args = parser.parse_args()
    try:
        spec = validate.unwrap(validate.read(args.spec))
    except (OSError, ValueError) as unreadable:
        print(args.spec + ": can't read it as JSON: " + str(unreadable))
        return 1
    found, _ = validate.check(spec)
    if found:
        print("\n".join(found))
        return 1
    try:
        sized = dict(spec)
        if not any(key in sized for key in SEVERAL):
            sized.setdefault("width", 560)
            sized.setdefault("height", 260)
        png = vl_convert.vegalite_to_png(sized, scale=args.scale, config=LOOK, allowed_base_urls=[])
    except Exception as failed:
        print("spec: couldn't draw it: " + validate.why(failed))
        return 1
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(png)
    print("wrote " + str(out) + " (" + str(len(png) // 1024) + " KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
