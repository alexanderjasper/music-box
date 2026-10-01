"""Lay square images onto a sheet of die-cut labels and return a PDF.

Shared by the `/labels` page in the config app and by `tools/labels.py`, so the
sheet geometry lives in exactly one place.

The geometry is measured off the vendor's own template (etiketlageret A4-12,
Skabelon_12-3.pdf) by rendering it at 1 px/mm: labels 60 x 60 mm with 5 mm
gutters, 10 mm from the left and 20 mm from the top of an A4 page. The stock is a
little shorter than A4, so the slack sits at the bottom — hence anchoring the grid
to the top-left, which is also how printers feed.

Images are embedded as JPEG using PDF's own DCTDecode, so no PDF library is
needed. Scaling and cropping go through Pillow when it is installed (the Pi) and
fall back to macOS's built-in `sips` otherwise.
"""

import io
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
import zlib

MM = 72.0 / 25.4              # mm -> PDF points

SHEET  = (210.0, 297.0)
LABEL  = (60.0, 60.0)
COLS, ROWS = 3, 4
MARGIN = (10.0, 20.0)         # left, top
GUTTER = (5.0, 5.0)
SLOTS  = COLS * ROWS

TARGET_PX = 720               # 60 mm at ~300 ppi
MIN_PX = 470                  # below this, 60 mm looks soft (< 200 ppi)


def default_geometry(**over):
    geom = {"left": MARGIN[0], "top": MARGIN[1],
            "gx": GUTTER[0], "gy": GUTTER[1], "dx": 0.0, "dy": 0.0}
    geom.update({k: v for k, v in over.items() if v is not None})
    return geom


def slot_box(slot, geom):
    """A label's box in mm as (x, y, w, h), y from the sheet's bottom."""
    col = (slot - 1) % COLS
    row = (slot - 1) // COLS
    x = geom["left"] + col * (LABEL[0] + geom["gx"]) + geom["dx"]
    y_top = geom["top"] + row * (LABEL[1] + geom["gy"]) - geom["dy"]
    return x, SHEET[1] - y_top - LABEL[1], LABEL[0], LABEL[1]


# --- turning any image into a square JPEG -----------------------------------

def _have_pillow():
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


def _prep_pillow(data):
    from PIL import Image
    im = Image.open(io.BytesIO(data))
    im.draft("RGB", (TARGET_PX, TARGET_PX))   # cheap DCT downscale for JPEGs
    im = im.convert("RGB")
    side = min(im.size)
    left, top = (im.width - side) // 2, (im.height - side) // 2
    im = im.crop((left, top, left + side, top + side))
    if side > TARGET_PX:
        im = im.resize((TARGET_PX, TARGET_PX), Image.LANCZOS)
    out = io.BytesIO()
    im.save(out, "JPEG", quality=88)
    return out.getvalue(), im.width, im.height, side


def _sips(*args):
    r = subprocess.run(["sips", *args], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"sips failed: {r.stderr.strip()}")
    return r.stdout


def _prep_sips(data):
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "src")
        work = os.path.join(tmp, "out.jpg")
        open(src, "wb").write(data)
        props = _sips("-g", "pixelWidth", "-g", "pixelHeight", "-g", "space", src)
        get = lambda k: re.search(rf"{k}:\s*(\S+)", props).group(1)
        side = min(int(get("pixelWidth")), int(get("pixelHeight")))
        if get("space") == "CMYK":
            raise ValueError("CMYK images are not supported — convert to RGB")
        _sips("-s", "format", "jpeg", "-s", "formatOptions", "88",
              src, "--out", work)
        _sips("-c", str(side), str(side), work)              # crops centred
        if side > TARGET_PX:
            _sips("-Z", str(TARGET_PX), work)
        q = _sips("-g", "pixelWidth", "-g", "pixelHeight", work)
        w = int(re.search(r"pixelWidth:\s*(\d+)", q).group(1))
        h = int(re.search(r"pixelHeight:\s*(\d+)", q).group(1))
        return open(work, "rb").read(), w, h, side


def prepare(data):
    """Square, downscaled JPEG bytes plus (width, height, source_side)."""
    if _have_pillow():
        return _prep_pillow(data)
    if shutil.which("sips"):
        return _prep_sips(data)
    raise RuntimeError("need Pillow (pip install pillow) or macOS sips")


# --- the smallest PDF that can place images and text ------------------------

class _Pdf:
    def __init__(self):
        self.objects = [None]

    def add(self, body):
        self.objects.append(body)
        return len(self.objects) - 1

    def bytes(self, page_size, content_ref, resources):
        pages, page, catalog = self.add(b""), self.add(b""), self.add(b"")
        w, h = page_size[0] * MM, page_size[1] * MM
        self.objects[pages] = f"<< /Type /Pages /Kids [{page} 0 R] /Count 1 >>".encode()
        self.objects[page] = (
            f"<< /Type /Page /Parent {pages} 0 R /MediaBox [0 0 {w:.3f} {h:.3f}] "
            f"/Resources << {resources} >> /Contents {content_ref} 0 R >>").encode()
        self.objects[catalog] = f"<< /Type /Catalog /Pages {pages} 0 R >>".encode()

        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = []
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
        for off in offsets:
            out += f"{off:010d} 00000 n \n".encode()
        out += (f"trailer\n<< /Size {len(self.objects)} /Root {catalog} 0 R >>\n"
                f"startxref\n{xref}\n%%EOF\n").encode()
        return bytes(out)


def build_sheet(images, bleed=1.0, geom=None, calib=False, infos=None):
    """The sheet as PDF bytes.

    images: {slot: raw image bytes} for the covers; infos: {slot: {"artist",
    "album", "tracks": [...]}} for the backs. Callers check cover sizes up front
    with `source_size`.
    """
    geom = geom or default_geometry()
    infos = infos or {}
    pdf = _Pdf()
    content, xobjects = [], []

    for i, slot in enumerate(sorted(images), start=1):
        data, iw, ih, _ = prepare(images[slot])
        ref = pdf.add((f"/Type /XObject /Subtype /Image /Width {iw} /Height {ih} "
                       f"/ColorSpace /DeviceRGB /BitsPerComponent 8 "
                       f"/Filter /DCTDecode", data))
        xobjects.append(f"/Im{i} {ref} 0 R")
        x, y, w, h = slot_box(slot, geom)
        x, y, w, h = x - bleed, y - bleed, w + 2 * bleed, h + 2 * bleed
        content.append(f"q {w*MM:.3f} 0 0 {h*MM:.3f} {x*MM:.3f} {y*MM:.3f} cm "
                       f"/Im{i} Do Q")

    for slot, info in sorted(infos.items()):
        content.extend(info_label(info, slot_box(slot, geom)))

    if calib:
        content.append("0.5 w 0.6 G")
        for slot in range(1, SLOTS + 1):
            x, y, w, h = slot_box(slot, geom)
            content.append(f"{x*MM:.3f} {y*MM:.3f} {w*MM:.3f} {h*MM:.3f} re S")
            content.append(f"BT /F1 14 Tf 0 g {(x+3)*MM:.3f} {(y+h-7)*MM:.3f} "
                           f"Td ({slot}) Tj ET")

    stream = zlib.compress("\n".join(content).encode("ascii"))
    content_ref = pdf.add(("/Filter /FlateDecode", stream))

    resources = ""
    if xobjects:
        resources += f"/XObject << {' '.join(xobjects)} >> "
    if calib or infos:
        fonts = []
        for key, name in (("F1", "Helvetica"), ("F2", "Helvetica-Bold")):
            ref = pdf.add(f"<< /Type /Font /Subtype /Type1 /BaseFont /{name} "
                          f"/Encoding /WinAnsiEncoding >>".encode())
            fonts.append(f"/{key} {ref} 0 R")
        resources += f"/Font << {' '.join(fonts)} >> "
    return pdf.bytes(SHEET, content_ref, resources)


# --- back labels: artist, album title, tracks --------------------------------
#
# Set in Helvetica, one of the fonts every PDF reader carries, so nothing is
# embedded and the text stays sharp at any printer resolution. Fitting it needs
# the glyph widths, which are Adobe's published metrics for WinAnsi codes
# 32-255 (from the Helvetica AFM files; 0 marks an unused code).

_HELVETICA = (
    278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278,
    278, 556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 278, 278, 584, 584,
    584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556,
    833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278,
    278, 278, 469, 556, 333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222,
    500, 222, 833, 556, 556, 556, 556, 333, 500, 278, 556, 500, 722, 500, 500,
    500, 334, 260, 334, 584, 0, 556, 0, 222, 556, 333, 1000, 556, 556, 333, 1000,
    667, 333, 1000, 0, 611, 0, 0, 222, 222, 333, 333, 350, 556, 1000, 333, 1000,
    500, 333, 944, 0, 500, 667, 278, 333, 556, 556, 556, 556, 260, 556, 333, 737,
    370, 556, 584, 333, 737, 333, 400, 584, 333, 333, 333, 556, 537, 278, 333,
    333, 365, 556, 834, 834, 834, 611, 667, 667, 667, 667, 667, 667, 1000, 722,
    667, 667, 667, 667, 278, 278, 278, 278, 722, 722, 778, 778, 778, 778, 778,
    584, 778, 722, 722, 722, 722, 667, 667, 611, 556, 556, 556, 556, 556, 556,
    889, 500, 556, 556, 556, 556, 278, 278, 278, 278, 556, 556, 556, 556, 556,
    556, 556, 584, 611, 556, 556, 556, 556, 500, 556, 500
)
_HELVETICA_BOLD = (
    278, 333, 474, 556, 556, 889, 722, 238, 333, 333, 389, 584, 278, 333, 278,
    278, 556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 333, 333, 584, 584,
    584, 611, 975, 722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611,
    833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 333,
    278, 333, 584, 556, 333, 556, 611, 556, 611, 556, 333, 611, 611, 278, 278,
    556, 278, 889, 611, 611, 611, 611, 389, 556, 333, 611, 556, 778, 556, 556,
    500, 389, 280, 389, 584, 0, 556, 0, 278, 556, 500, 1000, 556, 556, 333, 1000,
    667, 333, 1000, 0, 611, 0, 0, 278, 278, 500, 500, 350, 556, 1000, 333, 1000,
    556, 333, 944, 0, 500, 667, 278, 333, 556, 556, 556, 556, 280, 556, 333, 737,
    370, 556, 584, 333, 737, 333, 400, 584, 333, 333, 333, 611, 556, 278, 333,
    333, 365, 556, 834, 834, 834, 611, 722, 722, 722, 722, 722, 722, 1000, 722,
    667, 667, 667, 667, 278, 278, 278, 278, 722, 722, 778, 778, 778, 778, 778,
    584, 778, 722, 722, 722, 722, 667, 667, 611, 556, 556, 556, 556, 556, 556,
    889, 556, 556, 556, 556, 556, 278, 278, 278, 278, 611, 611, 611, 611, 611,
    611, 611, 584, 611, 611, 611, 611, 611, 556, 611, 556
)
_FONTS = {"F1": _HELVETICA, "F2": _HELVETICA_BOLD}

INFO_PAD = 4.5        # mm of white inside the die cut
ELLIPSIS = "\u2026"


def _winansi(text):
    """The text as WinAnsi bytes; what it lacks loses its accent, or becomes ?."""
    out = bytearray()
    for ch in unicodedata.normalize("NFC", str(text)):
        try:
            b = ch.encode("cp1252")
        except UnicodeEncodeError:
            bare = unicodedata.normalize("NFKD", ch).encode("ascii", "ignore")
            b = bare or b"?"
        out += bytes(c for c in b if c >= 32) or b""
    return bytes(out)


def text_width(text, font, size, spacing=0.0):
    """Width in points of `text` set in `font` ("F1"/"F2") at `size`."""
    table = _FONTS[font]
    raw = _winansi(text)
    return sum(table[b - 32] for b in raw) * size / 1000 + spacing * len(raw)


def _fit(text, font, size, width, spacing=0.0):
    """`text`, cut short with an ellipsis if it is wider than `width`."""
    if text_width(text, font, size, spacing) <= width:
        return text
    while text and text_width(text + ELLIPSIS, font, size, spacing) > width:
        text = text[:-1]
    return text.rstrip() + ELLIPSIS


def _wrap(text, font, size, width, lines):
    """Up to `lines` lines of `text` within `width`; the last cut if need be."""
    words, out = str(text).split(), []
    while words and len(out) < lines:
        line = words.pop(0)
        while words and text_width(f"{line} {words[0]}", font, size) <= width:
            line = f"{line} {words.pop(0)}"
        out.append(line)
    if words:
        out[-1] = _fit(f"{out[-1]} {' '.join(words)}", font, size, width)
    return [_fit(line, font, size, width) for line in out]


def _show(font, size, x, y, text, gray=0.0, spacing=0.0):
    raw = _winansi(text)
    esc = "".join(chr(b) if 32 <= b < 127 and b not in b"()\\" else f"\\{b:03o}"
                  for b in raw)
    # Tc is always set: it is graphics state, so it outlives ET into later text
    return (f"BT /{font} {size:.2f} Tf {gray:.2f} g {spacing:.2f} Tc "
            f"{x:.3f} {y:.3f} Td ({esc}) Tj ET")


def _track_layout(count, height):
    """(columns, size) for `count` tracks in `height` points: as big as fits."""
    def best(cols, sizes):
        rows = -(-count // cols)
        return next((s for s in sizes if rows * s * 1.3 <= height), None)

    one = best(1, [x / 4 for x in range(28, 17, -1)])     # 7 .. 4.5 pt
    if one is not None and one >= 5.0:
        return 1, one
    two = best(2, [x / 4 for x in range(24, 15, -1)])     # 6 .. 4 pt
    if two is not None:
        return 2, two
    return 2, 4.0                                         # and the rest is cut


def info_label(info, box):
    """PDF drawing ops for one back label within `box` (mm, as slot_box gives)."""
    x, y, w, h = (v * MM for v in box)
    pad = INFO_PAD * MM
    left, right, top = x + pad, x + w - pad, y + h - pad
    width = right - left
    ops = []

    artist = str(info.get("artist") or "").strip()
    album = str(info.get("album") or "").strip()
    tracks = [str(t).strip() for t in info.get("tracks") or [] if str(t).strip()]

    cursor = top
    if artist:
        size, spacing = 6.5, 0.5
        cursor -= size * 0.8
        ops.append(_show("F1", size, left, cursor,
                         _fit(artist.upper(), "F1", size, width, spacing),
                         gray=0.4, spacing=spacing))
        cursor -= size * 0.75
    if album:
        size = next((s for s in (11, 10.5, 10, 9.5, 9, 8.5, 8)
                     if len(_wrap(album, "F2", s, width, 3)) <= 2
                     and not _wrap(album, "F2", s, width, 3)[-1].endswith(ELLIPSIS)), 8)
        for line in _wrap(album, "F2", size, width, 2):
            cursor -= size * 0.95
            ops.append(_show("F2", size, left, cursor, line))
            cursor -= size * 0.2
    if not tracks:
        return ops

    cursor -= 2.6
    ops.append(f"0.4 w 0.7 G {left:.3f} {cursor:.3f} m {right:.3f} {cursor:.3f} l S")
    cursor -= 3.2

    cols, size = _track_layout(len(tracks), cursor - (y + pad))
    lead = size * 1.3
    rows = int((cursor - (y + pad)) // lead)
    if cols * rows < len(tracks):          # too many even at the smallest size
        keep = cols * rows - 1
        tracks = tracks[:keep] + [f"{ELLIPSIS} and {len(tracks) - keep} more"]
    per_col = -(-len(tracks) // cols)
    gap = 2.5 * MM
    col_w = (width - gap * (cols - 1)) / cols
    num_w = text_width(str(len(tracks)), "F1", size) + size * 0.6
    for i, title in enumerate(tracks):
        col, row = divmod(i, per_col)
        cx = left + col * (col_w + gap)
        base = cursor - size * 0.8 - row * lead
        more = title.startswith(ELLIPSIS)
        if not more:
            num = str(i + 1)
            ops.append(_show("F1", size, cx + num_w - size * 0.6
                             - text_width(num, "F1", size), base, num, gray=0.55))
        ops.append(_show("F1", size, cx + (0 if more else num_w), base,
                         _fit(title, "F1", size, col_w - (0 if more else num_w)),
                         gray=0.4 if more else 0.0))
    return ops


def source_size(data):
    """The source image's square side in pixels, for a quality warning."""
    try:
        return prepare(data)[3]
    except Exception:
        return 0
