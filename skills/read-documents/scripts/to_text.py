"""Turn a document into Markdown text, tables included.

PDF (with OCR for scanned pages), Word (.docx, and .doc/.rtf/.odt through LibreOffice), Excel (.xlsx, .xls, .ods,
.csv) and PowerPoint (.pptx, and .ppt/.odp through LibreOffice); anything else markitdown reads (HTML, EPUB, ...).
Writes the text to --out and prints one line saying what it wrote.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import warnings

LIBREOFFICE = {".doc": "docx", ".rtf": "docx", ".odt": "docx", ".ppt": "pptx", ".odp": "pptx"}
SHEETS = {".xlsx", ".xlsm", ".xls", ".ods", ".csv"}


def cell(value):
    """A table cell as one line of Markdown."""
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() == "nan":
        return ""
    return text.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def table(rows):
    """Rows (the first is the header) as a Markdown table; empty rows and columns dropped."""
    rows = [[cell(v) for v in row] for row in rows]
    rows = [row for row in rows if any(row)]
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]
    keep = [i for i in range(width) if any(row[i] for row in rows)]
    rows = [[row[i] for i in keep] for row in rows]
    lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * len(keep)]
    lines += ["| " + " | ".join(row) + " |" for row in rows[1:]]
    return "\n".join(lines)


def ocr(path, page_number):
    """A scanned PDF page's text, read by tesseract from a picture of it."""
    with tempfile.TemporaryDirectory() as tmp:
        prefix = os.path.join(tmp, "page")
        subprocess.run(["pdftoppm", "-r", "300", "-png", "-f", str(page_number), "-l", str(page_number), path, prefix],
                       check=True, capture_output=True)
        images = sorted(os.listdir(tmp))
        if not images:
            return ""
        done = subprocess.run(["tesseract", os.path.join(tmp, images[0]), "-"], check=True, capture_output=True, text=True)
        return done.stdout.strip()


def read_pdf(path, pages):
    import pdfplumber

    parts, stats = [], {"pages": 0, "tables": 0, "ocr": 0}
    with pdfplumber.open(path) as pdf:
        numbers = pages or range(1, len(pdf.pages) + 1)
        for number in numbers:
            if number < 1 or number > len(pdf.pages):
                continue
            page = pdf.pages[number - 1]
            stats["pages"] += 1
            tables = page.find_tables()
            # The page's text without its tables' words (a character whose middle is in a table), then each table.
            boxes = [found.bbox for found in tables]
            outside = page.filter(lambda obj: not any(
                x0 <= (obj.get("x0", 0) + obj.get("x1", 0)) / 2 <= x1 and top <= (obj.get("top", 0) + obj.get("bottom", 0)) / 2 <= bottom
                for x0, top, x1, bottom in boxes)) if boxes else page
            text = (outside.extract_text() or "").strip()
            if not text and not tables and shutil.which("tesseract") and shutil.which("pdftoppm"):
                text = ocr(path, number)
                if text:
                    stats["ocr"] += 1
                    text = "(read by OCR: check names and numbers)\n\n" + text
            body = [text] if text else []
            for found in tables:
                markdown = table(found.extract())
                if markdown:
                    body.append(markdown)
                    stats["tables"] += 1
            parts.append("## Page " + str(number) + "\n\n" + ("\n\n".join(body) if body else "(no text on this page)"))
        if not parts:
            raise ValueError("the PDF has " + str(len(pdf.pages)) + " pages, and none of those asked for")
    return "\n\n".join(parts), stats


def read_docx(path):
    import docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    document = docx.Document(path)
    parts, stats = [], {"tables": 0}
    # Paragraphs and tables in the order they come in the document.
    for block in document.element.body.iterchildren():
        tag = block.tag.rsplit("}", 1)[-1]
        if tag == "p":
            paragraph = Paragraph(block, document)
            text = paragraph.text.strip()
            if not text:
                continue
            style = (paragraph.style.name or "") if paragraph.style is not None else ""
            if style.startswith("Heading") and style[-1:].isdigit():
                text = "#" * min(int(style[-1]), 6) + " " + text
            elif style.startswith("List"):
                text = "- " + text
            parts.append(text)
        elif tag == "tbl":
            markdown = table([[c.text for c in row.cells] for row in Table(block, document).rows])
            if markdown:
                parts.append(markdown)
                stats["tables"] += 1
    return "\n\n".join(parts), stats


def read_pptx(path):
    from pptx import Presentation

    parts, stats = [], {"slides": 0, "tables": 0}
    for number, slide in enumerate(Presentation(path).slides, start=1):
        stats["slides"] += 1
        body = []
        for shape in slide.shapes:
            if shape.has_text_frame and shape.text_frame.text.strip():
                body.append(shape.text_frame.text.strip())
            if getattr(shape, "has_table", False) and shape.has_table:
                markdown = table([[c.text for c in row.cells] for row in shape.table.rows])
                if markdown:
                    body.append(markdown)
                    stats["tables"] += 1
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame.text.strip():
            body.append("Notes: " + slide.notes_slide.notes_text_frame.text.strip())
        parts.append("## Slide " + str(number) + "\n\n" + ("\n\n".join(body) if body else "(no text on this slide)"))
    return "\n\n".join(parts), stats


def read_sheets(path, extension):
    import pandas

    if extension == ".csv":
        sheets = {"CSV": pandas.read_csv(path, header=None, dtype=str, keep_default_na=False)}
    else:
        sheets = pandas.read_excel(path, sheet_name=None, header=None, dtype=str)
    parts, stats = [], {"sheets": 0, "tables": 0}
    for name, frame in sheets.items():
        stats["sheets"] += 1
        markdown = table(frame.values.tolist())
        if markdown:
            stats["tables"] += 1
        parts.append("## Sheet: " + str(name) + "\n\n" + (markdown or "(empty)"))
    return "\n\n".join(parts), stats


def read_other(path):
    from markitdown import MarkItDown

    return MarkItDown().convert(path).text_content.strip(), {}


def converted(path, target, tmp):
    """{@code path} turned into a {@code target} file by LibreOffice, in {@code tmp}."""
    subprocess.run(["soffice", "--headless", "--convert-to", target, "--outdir", tmp, path],
                   check=True, capture_output=True, timeout=180)
    name = os.path.splitext(os.path.basename(path))[0] + "." + target
    return os.path.join(tmp, name)


def page_numbers(text):
    """'1-3,7' as [1, 2, 3, 7]."""
    if not text:
        return None
    numbers = []
    for part in text.split(","):
        start, _, end = part.strip().partition("-")
        numbers += range(int(start), int(end or start) + 1)
    return numbers


def read(path, pages):
    extension = os.path.splitext(path)[1].lower()
    if extension == ".pdf":
        return read_pdf(path, pages)
    if extension in SHEETS:
        return read_sheets(path, extension)
    if extension in LIBREOFFICE:
        with tempfile.TemporaryDirectory() as tmp:
            # LibreOffice keeps a profile; a fresh one per run never clashes with another run.
            os.environ.setdefault("HOME", tmp)
            return read(converted(path, LIBREOFFICE[extension], tmp), pages)
    if extension == ".docx":
        return read_docx(path)
    if extension == ".pptx":
        return read_pptx(path)
    return read_other(path)


def main():
    parser = argparse.ArgumentParser(description="Turn a document into Markdown text, tables included.")
    parser.add_argument("file", help="the document, in the workspace")
    parser.add_argument("--out", required=True, help="the .md file to write, in the workspace")
    parser.add_argument("--pages", help="for a PDF, the pages to read, e.g. 1-3,7 (all when left out)")
    args = parser.parse_args()
    # Libraries' deprecation notes are not about the document.
    warnings.simplefilter("ignore")
    if not os.path.isfile(args.file):
        sys.exit("There is no file " + args.file)
    try:
        text, stats = read(args.file, page_numbers(args.pages))
    except subprocess.CalledProcessError as failed:
        sys.exit("Couldn't read " + args.file + ": " + (failed.stderr or b"").decode(errors="replace").strip()[-300:])
    except Exception as failed:  # a damaged or password-protected file, or one no reader takes
        sys.exit("Couldn't read " + args.file + ": " + type(failed).__name__ + ": " + str(failed)[:300])
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as out:
        out.write(text + "\n")
    said = ", ".join(str(v) + " " + k for k, v in stats.items() if v)
    print("Wrote " + args.out + ": " + str(len(text)) + " characters" + (", " + said if said else "")
          + ("" if text.strip() else ". No text was found"))


if __name__ == "__main__":
    main()
