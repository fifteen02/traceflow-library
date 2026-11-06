"""A document in the house style, as an A4 PDF: its content (JSON, as layouts/*.json shows) laid into the house's page.

    python3 render_pdf.py <document.json> <out.pdf> [--html <out.html>]

The content says what the document says; the page, type, colours, name and mark come from the house (style.py), so
every document looks like the others. Draws with Chromium (Playwright), its font embedded. Prints the page count.
"""
import base64
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

from style import ASSETS, DEFAULT_FONT, FALLBACK_FONTS, house

# A font family's name as Google Fonts spells it.
FAMILY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ]{0,60}$")

ESC = html.escape


def inline(text):
    """Words with **bold** and ==highlight== kept: everything else escaped."""
    out = ESC(str(text or ""))
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    return re.sub(r"==(.+?)==", r"<mark>\1</mark>", out)


def checklist(block):
    sections = []
    for section in block.get("sections", []):
        items = "".join(f'<li><i class="box"></i>{inline(item)}</li>' for item in section.get("items", []))
        sections.append(f'<section class="list"><h3>{ESC(section.get("title", ""))}<span>{len(section.get("items", []))}</span></h3>'
                        f'<ul>{items}</ul></section>')
    columns = 2 if block.get("columns", 2) == 2 else 1
    return f'<div class="cols cols-{columns}">{"".join(sections)}</div>'


def schedule(block):
    out = []
    for day in block.get("days", []):
        rows = ""
        for item in day.get("items", []):
            title = inline(item.get("title", ""))
            title = "<mark>" + title + "</mark>" if item.get("highlight") else title
            detail = "<i>" + inline(item["detail"]) + "</i>" if item.get("detail") else ""
            rows += (f'<div class="slot"><span class="time">{ESC(item.get("time", ""))}</span>'
                     f'<div><b>{title}</b>{detail}</div></div>')
        note = f'<span>{ESC(day["note"])}</span>' if day.get("note") else ""
        out.append(f'<section class="day"><h3>{ESC(day.get("title", ""))}{note}</h3>{rows}</section>')
    return "".join(out)


def figures(block):
    cells = "".join(f'<div><b>{ESC(item.get("value", ""))}</b>{ESC(item.get("label", ""))}</div>' for item in block.get("items", []))
    return f'<div class="figures">{cells}</div>'


def bars(block):
    items = block.get("items", [])
    most = max([float(item.get("value", 0)) for item in items] or [1]) or 1
    rows = ""
    for item in items:
        best = "best" if item.get("best") else ""
        width = max(2, round(float(item.get("value", 0)) / most * 100))
        shown = ESC(str(item.get("shown", item.get("value", ""))))
        rows += (f'<div class="bar"><span>{ESC(item.get("label", ""))}</span><span class="track"><i class="{best}" '
                 f'style="width:{width}%"></i></span><span class="value">{shown}</span></div>')
    unit = f'<span>{ESC(block["unit"])}</span>' if block.get("unit") else ""
    return f'<section class="bars"><h3>{ESC(block.get("title", ""))}{unit}</h3>{rows}</section>'


def compare(block):
    options = []
    for option in block.get("options", []):
        rows = "".join(f'<div class="row"><span>{ESC(k)}</span><span>{ESC(v)}</span></div>' for k, v in option.get("rows", []))
        tag = f'<span class="tag">{ESC(option.get("tag", "Best"))}</span>' if option.get("best") else ""
        options.append(f'<div class="option"><div class="name">{ESC(option.get("name", ""))}{tag}</div>'
                       f'<div class="figure">{ESC(option.get("figure", ""))}</div><div class="unit">{ESC(option.get("unit", ""))}</div>'
                       f'<div class="rows">{rows}</div></div>')
    verdict = f'<p class="verdict">{inline(block["verdict"])}</p>' if block.get("verdict") else ""
    return f'<div class="compare n{len(options)}">{"".join(options)}</div>{verdict}'


def table(block):
    numeric = ["num" if column.get("numeric") else "" for column in block.get("columns", [])]
    head = "".join(f'<th class="{numeric[i]}">{ESC(column.get("label", ""))}</th>' for i, column in enumerate(block.get("columns", [])))
    body = "".join("<tr>" + "".join(f'<td class="{numeric[i] if i < len(numeric) else ""}">{inline(cell)}</td>'
                                    for i, cell in enumerate(row)) + "</tr>" for row in block.get("rows", []))
    title = f'<h3>{ESC(block["title"])}</h3>' if block.get("title") else ""
    return f'<section class="table">{title}<table><tr>{head}</tr>{body}</table></section>'


BLOCKS = {
    "checklist": checklist, "schedule": schedule, "figures": figures, "bars": bars, "compare": compare, "table": table,
    "text": lambda block: f'<p class="text">{inline(block.get("text", ""))}</p>',
    "note": lambda block: f'<p class="note"><mark>{ESC(block.get("label", "Note"))}</mark> {inline(block.get("text", ""))}</p>',
    "heading": lambda block: f'<h2>{ESC(block.get("text", ""))}</h2>',
    "source": lambda block: f'<p class="source">{inline(block.get("text", ""))}</p>',
}


def when(value):
    try:
        day = date.fromisoformat(str(value)[:10])
        return f"{day.day} {day.strftime('%b %Y')}"
    except ValueError:
        return str(value or "")


def font_faces(family):
    """The page's font: a family the skill bundles (assets/fonts), embedded so the page needs no network; any other
    from Google Fonts, when the computer is online; without either, the fallbacks."""
    folder = ASSETS / "fonts" / family.lower().replace(" ", "-")
    if folder.is_dir():
        faces = ""
        for face in sorted(folder.glob("*.ttf")):
            data = base64.b64encode(face.read_bytes()).decode()
            faces += '@font-face{font-family:"%s";font-weight:%s;src:url(data:font/ttf;base64,%s)}' % (family, face.stem, data)
        return "<style>" + faces + "</style>"
    return ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=%s:wght@400;500;600&display=block">'
            % family.replace(" ", "+"))


def page(doc, h):
    unknown = [block.get("type") for block in doc.get("blocks", []) if block.get("type") not in BLOCKS]
    if unknown:
        raise SystemExit(f"Unknown block types: {', '.join(map(str, unknown))}. Use: {', '.join(BLOCKS)}")
    body = "".join(BLOCKS[block["type"]](block) for block in doc.get("blocks", []))
    mark = h["wordmark"] or f'<span class="name">{ESC(h["name"])}</span>'
    meta_for = "For " + str(doc["for"]) if doc.get("for") else ""
    meta = " · ".join(part for part in [meta_for, when(doc.get("date", date.today().isoformat()))] if part)
    css = (ASSETS / "page.css").read_text()
    family = h["font"] if FAMILY.match(h["font"]) else DEFAULT_FONT
    fonts = font_faces(family)
    lede = "<p class=lede>" + inline(doc["lede"]) + "</p>" if doc.get("lede") else ""
    tokens = ";".join(f"--{key.replace('_', '-')}:{value}" for key, value in h.items() if isinstance(value, str) and value.startswith("#"))
    return (f'<!doctype html><html lang="{ESC(doc.get("lang", "en"))}"><head><meta charset="utf-8"><title>{ESC(doc.get("title", ""))}</title>'
            f'{fonts}<style>:root{{{tokens};--font:"{ESC(family)}",{FALLBACK_FONTS}}}{css}</style></head><body><main>'
            f'<header><div class="mark">{mark}</div><div class="meta">{ESC(meta)}</div></header>'
            f'<h1>{ESC(doc.get("title", ""))}</h1>{lede}'
            f'{body}<footer><span>{ESC(doc.get("footer", doc.get("title", "")))}</span><span>Made with {ESC(h["name"])}</span></footer>'
            f'</main></body></html>')


def main(argv):
    if len(argv) < 3:
        raise SystemExit(__doc__)
    doc = json.loads(Path(argv[1]).read_text())
    markup = page(doc, house())
    if "--html" in argv:
        Path(argv[argv.index("--html") + 1]).write_text(markup)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        tab = browser.new_page()
        tab.set_content(markup, wait_until="networkidle", timeout=20000)
        tab.evaluate("document.fonts.ready")
        tab.pdf(path=argv[2], format="A4", print_background=True, prefer_css_page_size=True)
        browser.close()
    from pypdf import PdfReader
    print(f"{argv[2]}: {len(PdfReader(argv[2]).pages)} page(s)")


if __name__ == "__main__":
    main(sys.argv)
