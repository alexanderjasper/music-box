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


def build_sheet(images, bleed=1.0, geom=None, calib=False):
    """images: {slot: raw image bytes}. Returns the PDF as bytes.

    Also returns nothing about quality — call `prepare` yourself, or read the
    `soft` list this attaches to the returned object? No: keep it simple and let
    callers check sizes up front with `check_quality`.
    """
    geom = geom or default_geometry()
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

    if calib:
        content.append("0.5 w 0.6 G")
        for slot in range(1, SLOTS + 1):
            x, y, w, h = slot_box(slot, geom)
            content.append(f"{x*MM:.3f} {y*MM:.3f} {w*MM:.3f} {h*MM:.3f} re S")
            content.append(f"BT /F1 14 Tf 0 g {(x+3)*MM:.3f} {(y+h-7)*MM:.3f} "
                           f"Td ({slot}) Tj ET")

    stream = zlib.compress("\n".join(content).encode())
    content_ref = pdf.add(("/Filter /FlateDecode", stream))

    resources = ""
    if xobjects:
        resources += f"/XObject << {' '.join(xobjects)} >> "
    if calib:
        font = pdf.add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        resources += f"/Font << /F1 {font} 0 R >> "
    return pdf.bytes(SHEET, content_ref, resources)


def source_size(data):
    """The source image's square side in pixels, for a quality warning."""
    try:
        return prepare(data)[3]
    except Exception:
        return 0
