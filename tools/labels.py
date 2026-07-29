#!/usr/bin/env python3
"""Lay images onto a sheet of die-cut square labels and write a print-ready PDF.

For the etiketlageret A4-12 sheet: 12 labels of 60 x 60 mm, 3 across, 4 down, on
a 210 x 295.3 mm sheet. Slots are numbered 1..12, left to right, top to bottom:

        1   2   3
        4   5   6
        7   8   9
       10  11  12

You name the slots, so a part-used sheet can be finished off later:

    ./labels.py out.pdf 5=cover.jpg 6=another.png
    ./labels.py --calib calib.pdf          # outlines + numbers, on plain paper

Print at 100% / "actual size" with no page scaling, or the alignment is lost.

No dependencies: images are embedded as JPEG (PDF's own DCTDecode), and anything
that is not already a JPEG is converted and centre-cropped with sips, which ships
with macOS.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zlib

MM = 72.0 / 25.4          # mm -> PDF points

# Measured off the vendor's own template (Skabelon_12-3.pdf) by rendering it at
# 1 px/mm: labels 60 x 60 with 5 mm gutters, 10 mm from the left, 20 mm from the
# top of an A4 page. The stock is a little shorter than A4, so the slack is at the
# bottom — which is why the grid is anchored to the top-left, as printers are.
SHEET  = (210.0, 297.0)
LABEL  = (60.0, 60.0)
COLS, ROWS = 3, 4
MARGIN = (10.0, 20.0)     # left, top
GUTTER = (5.0, 5.0)


def sips(*args):
    out = subprocess.run(["sips", *args], capture_output=True, text=True)
    if out.returncode:
        sys.exit(f"sips failed: {out.stderr.strip()}")
    return out.stdout


def image_props(path):
    txt = sips("-g", "pixelWidth", "-g", "pixelHeight", "-g", "format",
               "-g", "space", path)
    get = lambda k: (re.search(rf"{k}:\s*(\S+)", txt) or [None, None])[1]
    return {
        "w": int(get("pixelWidth")),
        "h": int(get("pixelHeight")),
        "format": get("format"),
        "space": get("space"),
    }


def prepare(path, tmpdir, index):
    """Return (jpeg_bytes, width, height, colorspace), square-cropped."""
    p = image_props(path)
    side = min(p["w"], p["h"])
    work = os.path.join(tmpdir, f"{index}.jpg")

    if p["format"] == "jpeg" and p["w"] == p["h"]:
        shutil.copy(path, work)          # already square: keep the original bytes
    else:
        shutil.copy(path, os.path.join(tmpdir, f"src{index}"))
        src = os.path.join(tmpdir, f"src{index}")
        sips("-s", "format", "jpeg", "-s", "formatOptions", "90", src, "--out", work)
        sips("-c", str(side), str(side), work)      # sips crops centred

    q = image_props(work)
    space = "DeviceGray" if q["space"] in ("W", "Gray") else "DeviceRGB"
    if q["space"] == "CMYK":
        sys.exit(f"{path}: CMYK images are not supported — convert to RGB first")
    return open(work, "rb").read(), q["w"], q["h"], space


class Pdf:
    """The smallest PDF that can place images and text on one page."""

    def __init__(self):
        self.objects = [None]            # 1-indexed

    def add(self, body):
        self.objects.append(body)
        return len(self.objects) - 1

    def add_stream(self, dict_items, data):
        return self.add((dict_items, data))

    def write(self, path, page_size, content_ref, resources):
        pages = self.add(b"")            # placeholders, filled in below
        page = self.add(b"")
        catalog = self.add(b"")
        w, h = page_size[0] * MM, page_size[1] * MM
        self.objects[pages] = (
            f"<< /Type /Pages /Kids [{page} 0 R] /Count 1 >>".encode())
        self.objects[page] = (
            f"<< /Type /Page /Parent {pages} 0 R /MediaBox [0 0 {w:.3f} {h:.3f}] "
            f"/Resources << {resources} >> /Contents {content_ref} 0 R >>").encode()
        self.objects[catalog] = f"<< /Type /Catalog /Pages {pages} 0 R >>".encode()

        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for n, body in enumerate(self.objects[1:], start=1):
            offsets.append(len(out))
            out += f"{n} 0 obj\n".encode()
            if isinstance(body, tuple):
                items, data = body
                out += f"<< {items} /Length {len(data)} >>\nstream\n".encode()
                out += data + b"\nendstream\n"
            else:
                out += body + b"\n"
            out += b"endobj\n"
        xref = len(out)
        out += f"xref\n0 {len(self.objects)}\n0000000000 65535 f \n".encode()
        for off in offsets[1:]:
            out += f"{off:010d} 00000 n \n".encode()
        out += (f"trailer\n<< /Size {len(self.objects)} /Root {len(self.objects)-1} 0 R "
                f">>\nstartxref\n{xref}\n%%EOF\n").encode()
        open(path, "wb").write(bytes(out))


def slot_box(slot, geom):
    """The label's box in mm as (x, y, w, h), y measured from the sheet's bottom."""
    col = (slot - 1) % COLS
    row = (slot - 1) // COLS
    x = geom["left"] + col * (LABEL[0] + geom["gx"]) + geom["dx"]
    y_from_top = geom["top"] + row * (LABEL[1] + geom["gy"]) - geom["dy"]
    return x, SHEET[1] - y_from_top - LABEL[1], LABEL[0], LABEL[1]


def build(images, out_path, geom, bleed, calib):
    pdf = Pdf()
    content = []
    xobjects = []

    for i, (slot, path) in enumerate(images, start=1):
        data, iw, ih, space = prepare(path, geom["tmp"], i)
        name = f"Im{i}"
        ref = pdf.add_stream(
            f"/Type /XObject /Subtype /Image /Width {iw} /Height {ih} "
            f"/ColorSpace /{space} /BitsPerComponent 8 /Filter /DCTDecode", data)
        xobjects.append(f"/{name} {ref} 0 R")
        ppi = iw / (LABEL[0] / 25.4)
        if ppi < 200:
            print(f"note: {os.path.basename(path)} is {iw}px -> {ppi:.0f} ppi at "
                  f"60 mm; 470px+ is better", file=sys.stderr)
        x, y, w, h = slot_box(slot, geom)
        x, y, w, h = x - bleed, y - bleed, w + 2 * bleed, h + 2 * bleed
        content.append(f"q {w*MM:.3f} 0 0 {h*MM:.3f} {x*MM:.3f} {y*MM:.3f} cm "
                       f"/{name} Do Q")

    if calib:
        content.append("0.5 w 0.6 G")
        for slot in range(1, COLS * ROWS + 1):
            x, y, w, h = slot_box(slot, geom)
            content.append(f"{x*MM:.3f} {y*MM:.3f} {w*MM:.3f} {h*MM:.3f} re S")
            content.append(f"BT /F1 14 Tf 0 g {(x+3)*MM:.3f} {(y+h-7)*MM:.3f} "
                           f"Td ({slot}) Tj ET")
            content.append(f"BT /F1 7 Tf 0.4 g {(x+3)*MM:.3f} {(y+3)*MM:.3f} "
                           f"Td (60x60 at {x:.1f},{y:.1f} mm) Tj ET")

    stream = zlib.compress("\n".join(content).encode())
    content_ref = pdf.add_stream("/Filter /FlateDecode", stream)

    resources = ""
    if xobjects:
        resources += f"/XObject << {' '.join(xobjects)} >> "
    if calib:
        font = pdf.add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        resources += f"/Font << /F1 {font} 0 R >> "

    pdf.write(out_path, SHEET, content_ref, resources)


def main():
    ap = argparse.ArgumentParser(
        description="Place images on a sheet of 12 die-cut 60x60 mm labels.",
        epilog="slots are 1..12, left to right, top to bottom")
    ap.add_argument("out", help="the PDF to write")
    ap.add_argument("images", nargs="*", metavar="SLOT=IMAGE",
                    help="e.g. 5=cover.jpg — repeat for each label")
    ap.add_argument("--calib", action="store_true",
                    help="also draw the label outlines and slot numbers")
    ap.add_argument("--bleed", type=float, default=0.0, metavar="MM",
                    help="print this far past each label's edge (default 0)")
    ap.add_argument("--left", type=float, default=None, metavar="MM",
                    help=f"left margin (default {MARGIN[0]})")
    ap.add_argument("--top", type=float, default=None, metavar="MM",
                    help=f"top margin (default {MARGIN[1]})")
    ap.add_argument("--gap", type=float, nargs=2, default=GUTTER,
                    metavar=("X", "Y"), help=f"gutters between labels (default {GUTTER[0]} {GUTTER[1]})")
    ap.add_argument("--dx", type=float, default=0.0, metavar="MM",
                    help="nudge everything right")
    ap.add_argument("--dy", type=float, default=0.0, metavar="MM",
                    help="nudge everything down")
    args = ap.parse_args()

    gx, gy = args.gap
    geom = {
        "gx": gx, "gy": gy, "dx": args.dx, "dy": args.dy,
        "left": args.left if args.left is not None else MARGIN[0],
        "top": args.top if args.top is not None else MARGIN[1],
    }

    images = []
    for spec in args.images:
        if "=" not in spec:
            sys.exit(f"expected SLOT=IMAGE, got {spec!r}")
        slot, path = spec.split("=", 1)
        if not slot.isdigit() or not 1 <= int(slot) <= COLS * ROWS:
            sys.exit(f"slot must be 1..{COLS * ROWS}, got {slot!r}")
        if not os.path.exists(path):
            sys.exit(f"no such image: {path}")
        images.append((int(slot), path))

    if not images and not args.calib:
        sys.exit("nothing to do: give SLOT=IMAGE pairs, or --calib")

    with tempfile.TemporaryDirectory() as tmp:
        geom["tmp"] = tmp
        build(images, args.out, geom, args.bleed, args.calib)

    used = ", ".join(str(s) for s, _ in sorted(images)) or "none"
    print(f"{args.out}: slots {used}"
          f"{' + calibration grid' if args.calib else ''}")
    print(f"grid starts {geom['left']:.2f} mm from the left, "
          f"{geom['top']:.2f} mm from the top, gaps {gx} x {gy} mm")
    print("print at 100% — no 'fit to page', no scaling")


if __name__ == "__main__":
    main()
