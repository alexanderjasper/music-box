#!/usr/bin/env python3
"""Lay images onto a sheet of die-cut 60 x 60 mm labels and write a PDF.

The same job the box's /labels page does, for when the terminal is handier. Sheet
geometry and the PDF writing live in software/web/labelsheet.py.

    ./labels.py out.pdf 5=cover.jpg 6=other.png     # slots 1..12, L-R, top-bottom
    ./labels.py grid.pdf --calib                    # outlines, for plain paper

Print at 100% / "actual size", or the alignment is lost.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "software"))
from web import labelsheet  # noqa: E402


def main():
    ap = argparse.ArgumentParser(
        description="Place images on a sheet of 12 die-cut 60x60 mm labels.",
        epilog="slots are 1..%d, left to right, top to bottom" % labelsheet.SLOTS)
    ap.add_argument("out", help="the PDF to write")
    ap.add_argument("images", nargs="*", metavar="SLOT=IMAGE",
                    help="e.g. 5=cover.jpg — repeat for each label")
    ap.add_argument("--calib", action="store_true",
                    help="also draw the label outlines and slot numbers")
    ap.add_argument("--bleed", type=float, default=1.0, metavar="MM",
                    help="print this far past each label's edge (default 1.0; "
                         "the gutter allows up to 2.5, use 0 for exact size)")
    ap.add_argument("--left", type=float, metavar="MM", help="left margin")
    ap.add_argument("--top", type=float, metavar="MM", help="top margin")
    ap.add_argument("--dx", type=float, metavar="MM", help="nudge everything right")
    ap.add_argument("--dy", type=float, metavar="MM", help="nudge everything down")
    args = ap.parse_args()

    images = {}
    for spec in args.images:
        if "=" not in spec:
            sys.exit(f"expected SLOT=IMAGE, got {spec!r}")
        slot, path = spec.split("=", 1)
        if not slot.isdigit() or not 1 <= int(slot) <= labelsheet.SLOTS:
            sys.exit(f"slot must be 1..{labelsheet.SLOTS}, got {slot!r}")
        if not os.path.exists(path):
            sys.exit(f"no such image: {path}")
        data = open(path, "rb").read()
        if labelsheet.source_size(data) < labelsheet.MIN_PX:
            print(f"note: {os.path.basename(path)} is small; 60 mm will look soft",
                  file=sys.stderr)
        images[int(slot)] = data

    if not images and not args.calib:
        sys.exit("nothing to do: give SLOT=IMAGE pairs, or --calib")

    geom = labelsheet.default_geometry(left=args.left, top=args.top,
                                       dx=args.dx, dy=args.dy)
    pdf = labelsheet.build_sheet(images, bleed=args.bleed, geom=geom,
                                 calib=args.calib)
    open(args.out, "wb").write(pdf)
    print(f"{args.out}: slots {', '.join(str(s) for s in sorted(images)) or 'none'}"
          f"{' + calibration grid' if args.calib else ''}")
    print("print at 100% — no 'fit to page', no scaling")


if __name__ == "__main__":
    main()
