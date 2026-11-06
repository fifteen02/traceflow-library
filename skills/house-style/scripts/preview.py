"""Page one of a PDF as a PNG, to look at before handing the file over (view_image it).

    python3 preview.py <in.pdf> <out.png> [page]

Uses pypdfium2. Prints the page count, so a one-pager that ran onto a second page shows at once.
"""
import sys

import pypdfium2 as pdfium


def main(argv):
    if len(argv) < 3:
        raise SystemExit(__doc__)
    pdf = pdfium.PdfDocument(argv[1])
    index = int(argv[3]) - 1 if len(argv) > 3 else 0
    pdf[index].render(scale=1.6).to_pil().save(argv[2])
    print(f"{argv[2]}: page {index + 1} of {len(pdf)}")


if __name__ == "__main__":
    main(sys.argv)
