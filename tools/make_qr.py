"""Make a QR code for the live portfolio.

A QR code is just your URL turned into a picture of black and white squares.
A phone camera reads the pattern and opens the address - so the only thing
that matters is that the URL inside it is correct and permanent.

Two files come out of this script:

    qr/portfolio-qr.png       print-ready, pure black on white, square
    qr/portfolio-qr-card.png  a dark card with the name and link, for
                              sharing on screen (story, chat, slide)

Run it with:

    python tools/make_qr.py

The script decodes both images again with a second, independent library and
refuses to finish if the text inside them is not exactly the URL. That is the
step that stops you printing 100 flyers with a broken code on them.
"""

import sys
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "qr"

URL = "https://cjadebadua117-sys.github.io/"
NAME = "Christian Jade Badua"
ROLE = "Information Systems  ·  Django developer"
SHOWN_URL = "cjadebadua117-sys.github.io"

# Error correction H survives about 30% of the code being damaged; it is the
# right choice for anything that gets printed, folded or photographed.
ERROR = ERROR_CORRECT_H
BORDER = 4  # modules of white space around the code - the "quiet zone"

INK = (0, 0, 0)
PAPER = (255, 255, 255)

CARD_BG = (13, 15, 18)
CARD_INK = (244, 245, 247)
CARD_MUTED = (150, 158, 170)

TARGET_PX = 1200  # roughly 10 cm at 300 dpi, plenty for a resume


def build_matrix(text: str):
    """Return the QR as a list of rows of True/False (True = black)."""
    qr = qrcode.QRCode(error_correction=ERROR, border=BORDER, box_size=1)
    qr.add_data(text)
    qr.make(fit=True)
    return qr.get_matrix()


def render_square(matrix, px: int) -> Image.Image:
    """Draw the matrix at an exact, undistorted module size.

    Scaling a small QR up with interpolation blurs module edges and is a
    common reason codes fail to scan. Building it at the final size avoids
    that completely.
    """
    modules = len(matrix)
    box = max(1, round(px / modules))  # integer pixels per module
    size = modules * box
    img = Image.new("RGB", (size, size), PAPER)
    draw = ImageDraw.Draw(img)
    for y, row in enumerate(matrix):
        for x, cell in enumerate(row):
            if cell:
                draw.rectangle(
                    [x * box, y * box, (x + 1) * box - 1, (y + 1) * box - 1],
                    fill=INK,
                )
    return img


def font(name: str, size: int):
    """Use a real Windows font when available, otherwise fall back."""
    for candidate in (name, "segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def centered(draw, y, text, f, fill, width):
    left = (width - draw.textlength(text, font=f)) / 2
    draw.text((left, y), text, font=f, fill=fill)


def render_card(qr_img: Image.Image) -> Image.Image:
    """A shareable card: dark background, the code in a white panel."""
    W, H = 1080, 1350
    card = Image.new("RGB", (W, H), CARD_BG)
    d = ImageDraw.Draw(card)

    # thin frame
    d.rectangle([48, 48, W - 49, H - 49], outline=(38, 42, 50), width=2)

    centered(d, 118, "PORTFOLIO", font("consola.ttf", 26), CARD_MUTED, W)
    centered(d, 168, NAME, font("segoeuib.ttf", 62), CARD_INK, W)
    centered(d, 250, ROLE, font("segoeui.ttf", 30), CARD_MUTED, W)

    # white panel holding the code, so it scans from a dark screen too
    qr_size = 660
    qr_img = qr_img.resize((qr_size, qr_size), Image.NEAREST)
    pad = 28
    panel = qr_size + pad * 2
    x0 = (W - panel) // 2
    y0 = 380
    d.rounded_rectangle([x0, y0, x0 + panel, y0 + panel], radius=18, fill=PAPER)
    card.paste(qr_img, (x0 + pad, y0 + pad))

    centered(d, y0 + panel + 70, "Scan to open", font("segoeui.ttf", 30), CARD_MUTED, W)
    centered(d, y0 + panel + 118, SHOWN_URL, font("consola.ttf", 34), CARD_INK, W)

    return card


def verify(path: Path, expected: str) -> bool:
    """Read the saved image back with a different library and compare."""
    import zxingcpp

    results = zxingcpp.read_barcodes(Image.open(path))
    if not results:
        print(f"[FAIL] {path.name}: no QR code found in the image")
        return False
    got = results[0].text.strip()
    if got != expected:
        print(f"[FAIL] {path.name}: decodes to {got!r}, expected {expected!r}")
        return False
    print(f"[OK]   {path.name:24} -> {got}")

    # what a scanner reports about the format is a useful sanity check
    print(
        f"       format={results[0].format} "
        f"ecc={results[0].ec_level} "
        f"{Image.open(path).size[0]}x{Image.open(path).size[1]} px"
    )
    return True


def main() -> int:
    OUT.mkdir(exist_ok=True)
    print(f"encoding: {URL}")

    matrix = build_matrix(URL)
    print(f"          {len(matrix)}x{len(matrix)} modules, {BORDER} quiet-zone border")

    square = render_square(matrix, TARGET_PX)
    square_path = OUT / "portfolio-qr.png"
    square.save(square_path)

    card = render_card(square)
    card_path = OUT / "portfolio-qr-card.png"
    card.save(card_path)

    ok = verify(square_path, URL) & verify(card_path, URL)
    print()
    if not ok:
        print("[FAIL] a code does not decode correctly - do not print it")
        return 1
    print(f"[OK]   wrote {square_path.relative_to(ROOT)}")
    print(f"[OK]   wrote {card_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
