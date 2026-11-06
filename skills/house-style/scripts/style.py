"""The house style a document is made in: a deployment's settings (environment variables) over neutral defaults.

    HOUSE_NAME      who documents are made by: the header (in type, when there is no wordmark) and the footer
    HOUSE_WORDMARK  the name's mark as inline SVG; blank sets the name in type
    HOUSE_FONT      a font family: one the skill bundles (Inter, Instrument Sans, IBM Plex Sans, Source Serif 4), else
                    from Google Fonts when the computer is online
    HOUSE_INK       the darkest colour, a hex: text, rules, and every grey (mixed from it toward white)
    HOUSE_ACCENT    the one accent, a hex: the highlighter, the answer cell, the best option's tag

A setting left blank or set to `default` takes the default, which carries no brand: a neutral sans, near-black ink, a
grey highlight. A deployment's settings make the documents its own. Standard library only.
"""
import os
import re
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

DEFAULT_NAME = "traceflow"
DEFAULT_FONT = "Inter"
DEFAULT_INK = "#18181B"
DEFAULT_ACCENT = "#E4E4E7"
# What the page falls back to when the font can't be had: what the computer always has.
FALLBACK_FONTS = '"Liberation Sans", "DejaVu Sans", Arial, sans-serif'

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")

# Each grey the page uses, as the share of ink in it (the rest white).
GREYS = {"canvas": 0.045, "line": 0.075, "border": 0.12, "mute": 0.36, "faint": 0.50, "tertiary": 0.60,
         "secondary": 0.72, "body": 0.86}


def setting(name, default):
    value = os.environ.get(name, "").strip()
    return default if not value or value.lower() == "default" else value


def colour(name, default):
    value = setting(name, default)
    return value.upper() if HEX.match(value) else default


def mix(hex_colour, share):
    """`hex_colour` at `share`, the rest white."""
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    blend = lambda c: round(c * share + 255 * (1 - share))
    return "#{:02X}{:02X}{:02X}".format(blend(r), blend(g), blend(b))


def wordmark():
    """The mark's SVG when one is set and safe to place in a page: nothing that runs, nothing it fetches."""
    svg = setting("HOUSE_WORDMARK", "")
    if not svg.startswith("<svg") or not svg.endswith("</svg>") or len(svg) > 50_000:
        return None
    if re.search(r"<script|<foreignObject|\son\w+\s*=|javascript:|href\s*=\s*[\"'](?!#)", svg, re.IGNORECASE):
        return None
    return svg


def house():
    """Everything a document is drawn with."""
    ink = colour("HOUSE_INK", DEFAULT_INK)
    accent = colour("HOUSE_ACCENT", DEFAULT_ACCENT)
    return {
        "name": setting("HOUSE_NAME", DEFAULT_NAME),
        "wordmark": wordmark(),
        "font": setting("HOUSE_FONT", DEFAULT_FONT),
        "ink": ink,
        "page": "#FFFFFF",
        **{grey: mix(ink, share) for grey, share in GREYS.items()},
        "accent": accent,
        "accent_soft": mix(accent, 0.42),
    }
