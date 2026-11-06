"""A spreadsheet in the house style: its content (JSON, as layouts/budget.json shows) laid into styled sheets.

    python3 render_xlsx.py <sheet.json> <out.xlsx>

Each sheet: a title and a line under it, a header row, rows of cells. A cell is text, a number, or a formula ("=B3*C3");
a column's `kind` (text | money | number | percent | date) says how its numbers read. Cells listed in a row's
`inputs` are the reader's to change (the accent's pale twin); a row with `"total": true` is the answer (ink rule above,
the accent on its figures). Uses openpyxl; each formula's value is written beside it (LibreOffice works them out), so
the totals show in viewers that don't calculate, such as a phone's preview.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from xml.sax.saxutils import escape

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from style import house

FORMATS = {"money": '"€"#,##0;-"€"#,##0', "number": "#,##0.##", "percent": "0%", "date": "d mmm yyyy",
           "text": "@"}


# The row of each sheet's column headings; its rows follow.
HEAD_ROW = 4


def fill(hex_colour):
    return PatternFill("solid", fgColor=hex_colour.lstrip("#"))


def main(argv):
    if len(argv) < 3:
        raise SystemExit(__doc__)
    spec = json.loads(Path(argv[1]).read_text())
    h = house()
    font = h["font"]
    ink, line, canvas = h["ink"].lstrip("#"), h["line"].lstrip("#"), h["canvas"].lstrip("#")
    hair = Side(style="hair", color=line)
    rule = Side(style="thin", color=ink)
    currency = spec.get("currency", "€")
    book = Workbook()
    book.remove(book.active)
    for sheet in spec.get("sheets", []):
        ws = book.create_sheet(str(sheet.get("name", "Sheet"))[:31])
        ws.sheet_view.showGridLines = False
        columns = sheet.get("columns", [])
        ws["A1"] = sheet.get("title", spec.get("title", ""))
        ws["A1"].font = Font(name=font, size=18, color=ink)
        ws.row_dimensions[1].height = 30
        ws["A2"] = sheet.get("subtitle", spec.get("subtitle", ""))
        ws["A2"].font = Font(name=font, size=10, color=h["tertiary"].lstrip("#"))
        head = HEAD_ROW
        for index, column in enumerate(columns, start=1):
            cell = ws.cell(row=head, column=index, value=column.get("label", ""))
            cell.font = Font(name=font, size=10, bold=True, color=ink)
            cell.fill = fill(h["line"])
            cell.border = Border(bottom=rule)
            numeric = column.get("kind", "text") != "text"
            cell.alignment = Alignment(horizontal="right" if numeric else "left", vertical="center", indent=0 if numeric else 1)
            ws.column_dimensions[get_column_letter(index)].width = column.get("width", 14 if numeric else 28)
        ws.row_dimensions[head].height = 22
        for offset, row in enumerate(sheet.get("rows", []), start=1):
            at = head + offset
            total = row.get("total", False)
            inputs = set(row.get("inputs", []))
            ws.row_dimensions[at].height = 20
            for index, column in enumerate(columns, start=1):
                key = column.get("key", column.get("label"))
                value = row.get("cells", {}).get(key)
                cell = ws.cell(row=at, column=index, value=value)
                kind = column.get("kind", "text")
                if kind != "text":
                    cell.number_format = FORMATS.get(kind, "General").replace("€", currency)
                cell.font = Font(name=font, size=10, bold=total, color=ink if total or key in inputs else h["body"].lstrip("#"))
                cell.alignment = Alignment(horizontal="right" if kind != "text" else "left", vertical="center", indent=0 if kind != "text" else 1)
                cell.border = Border(top=rule) if total else Border(bottom=hair)
                if key in inputs:
                    cell.fill = fill(h["accent_soft"])
                elif total and kind != "text" and value not in (None, ""):
                    cell.fill = fill(h["accent"])
        if sheet.get("legend", True):
            at = head + len(sheet.get("rows", [])) + 2
            ws.cell(row=at, column=1, value="Yours to change").fill = fill(h["accent_soft"])
            ws.cell(row=at, column=2, value="The answer").fill = fill(h["accent"])
            for index in (1, 2):
                ws.cell(row=at, column=index).font = Font(name=font, size=9, color=h["tertiary"].lstrip("#"))
        ws.freeze_panes = ws.cell(row=head + 1, column=1)
        ws.sheet_properties.tabColor = canvas
        footer = ws.oddFooter
        footer.left.text, footer.right.text = sheet.get("title", spec.get("title", "")), f"Made with {h['name']}"
    book.properties.creator = h["name"]
    book.save(argv[2])
    said, worked_out = with_values(argv[2], book.sheetnames)
    Path(argv[2] + TABLE_SUFFIX).write_text(json.dumps(preview(spec, book.sheetnames, worked_out), ensure_ascii=False))
    print(f"{argv[2]}: {len(book.sheetnames)} sheet(s); {said}")


# The file beside a spreadsheet that a chat app draws it from, as a table in the conversation.
TABLE_SUFFIX = ".table.json"


def preview(spec, sheet_names, worked_out):
    """
    What a chat app draws the spreadsheet as: each sheet's title and line under it, its columns, and each row's cells
    as they read in the sheet ("€1,334"), with the ones the reader changes and the answer marked. No colours or fonts:
    the app draws it in its own.
    """
    currency = spec.get("currency", "€")
    sheets = []
    for sheet, name in zip(spec.get("sheets", []), sheet_names):
        columns = sheet.get("columns", [])
        values = worked_out.get(name, {})
        rows = []
        for offset, row in enumerate(sheet.get("rows", []), start=1):
            at = HEAD_ROW + offset
            cells = []
            for index, column in enumerate(columns, start=1):
                value = row.get("cells", {}).get(column.get("key", column.get("label")))
                if isinstance(value, str) and value.startswith("="):
                    value = values.get(f"{get_column_letter(index)}{at}")
                cells.append(reads(value, column.get("kind", "text"), currency))
            keys = [column.get("key", column.get("label")) for column in columns]
            rows.append({"cells": cells, "inputs": [keys.index(key) for key in row.get("inputs", []) if key in keys],
                         **({"total": True} if row.get("total") else {})})
        sheets.append({"name": name, "title": sheet.get("title", spec.get("title", "")),
                       "subtitle": sheet.get("subtitle", spec.get("subtitle", "")),
                       "columns": [{"label": column.get("label", ""), "numeric": column.get("kind", "text") != "text"}
                                   for column in columns],
                       "rows": rows})
    return {"sheets": sheets}


def reads(value, kind, currency):
    """A cell's value as its column's format shows it; empty for none."""
    if value is None or value == "":
        return ""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return str(value)
    if kind == "money":
        return ("-" if value < 0 else "") + currency + f"{int(Decimal(abs(value)).quantize(0, ROUND_HALF_UP)):,}"
    if kind == "percent":
        return f"{value:.0%}"
    if kind == "number":
        return f"{value:,.2f}".rstrip("0").rstrip(".")
    return f"{value:g}"


# A formula cell as openpyxl writes it: its formula, its value left empty.
FORMULA_CELL = re.compile(r'<c r="([A-Z]+[0-9]+)"([^>]*)><f>(.*?)</f><v></v></c>')


def with_values(path, sheet_names):
    """
    Each formula's value written beside it in the file at `path`, as LibreOffice works it out from a copy; nothing else
    in the file changes (its layout, styles and formulas stay as written). Says how it went: without LibreOffice, or
    when it fails, the formulas stay without values and work out once the file is opened in a spreadsheet app. With
    what it says, the values by sheet and cell ("D11"); none when it couldn't work them out.
    """
    soffice = shutil.which("soffice")
    if not soffice:
        return "no LibreOffice here, so its totals show once it is opened in a spreadsheet app", {}
    with tempfile.TemporaryDirectory() as work:
        env = {**os.environ, "SAL_USE_VCLPLUGIN": "svp", "HOME": work}
        try:
            subprocess.run([soffice, "--headless", "--norestore", f"-env:UserInstallation={Path(work, 'profile').as_uri()}",
                            "--convert-to", "xlsx:Calc MS Excel 2007 XML", "--outdir", work, path],
                           env=env, capture_output=True, timeout=180, check=False)
        except subprocess.TimeoutExpired:
            return "LibreOffice took too long, so its totals show once it is opened in a spreadsheet app", {}
        worked = Path(work) / Path(path).name
        if not worked.exists():
            return "LibreOffice couldn't work out its totals, so they show once it is opened in a spreadsheet app", {}
        values = load_workbook(worked, data_only=True)
        worked_out = {name: {cell.coordinate: cell.value for row in values[name].iter_rows() for cell in row}
                      for name in sheet_names if name in values.sheetnames}
        written = Path(work) / "with-values.xlsx"
        filled = 0
        with zipfile.ZipFile(path) as source, zipfile.ZipFile(written, "w", zipfile.ZIP_DEFLATED) as target:
            for item in source.infolist():
                data = source.read(item.filename)
                sheet = re.fullmatch(r"xl/worksheets/sheet(\d+)\.xml", item.filename)
                if sheet and int(sheet[1]) <= len(sheet_names):
                    known = values[sheet_names[int(sheet[1]) - 1]]
                    text = data.decode("utf-8")
                    filled += sum(1 for cell in FORMULA_CELL.finditer(text) if known[cell[1]].value is not None)
                    data = FORMULA_CELL.sub(lambda cell: valued(cell, known), text).encode("utf-8")
                target.writestr(item, data)
        shutil.move(written, path)
    return f"{filled} formula(s) worked out", worked_out


# The errors a formula can come to, as a spreadsheet writes them.
ERRORS = {"#NULL!", "#DIV/0!", "#VALUE!", "#REF!", "#NAME?", "#NUM!", "#N/A"}


def valued(cell, known):
    """A formula cell with the value LibreOffice gave it: a number, a yes/no, an error or text; left empty when it gave none."""
    where, attributes, formula = cell[1], cell[2], cell[3]
    value = known[where].value
    if isinstance(value, bool):
        return f'<c r="{where}"{attributes} t="b"><f>{formula}</f><v>{int(value)}</v></c>'
    if isinstance(value, (int, float)):
        return f'<c r="{where}"{attributes}><f>{formula}</f><v>{value!r}</v></c>'
    if value in ERRORS:
        return f'<c r="{where}"{attributes} t="e"><f>{formula}</f><v>{value}</v></c>'
    if isinstance(value, str):
        return f'<c r="{where}"{attributes} t="str"><f>{formula}</f><v>{escape(value)}</v></c>'
    return cell[0]


if __name__ == "__main__":
    main(sys.argv)
