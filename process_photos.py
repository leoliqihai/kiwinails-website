"""Batch convert HEIC product photos into clean web-ready PNGs.

Pipeline per file:
1. Convert HEIC -> high-res JPG using macOS `sips`.
2. Crop out the bottom label band and top-left watermark.
3. Use `rembg` to cut the product against the green background.
4. Composite onto a soft-shadow white background and save as PNG @ 1500px.

We deliberately KEEP a copy of the cropped label band as a separate file so
the SKU on it can still be cross-referenced manually later.
"""
import subprocess
import sys
from pathlib import Path

SRC = Path("/Users/yw19990803/Downloads/kiwinails images")
OUT_DIR = Path(__file__).parent / "kiwinails-website" / "assets" / "images" / "products" / "photos"
OUT_DIR.mkdir(parents=True, exist_ok=True)
LABELS_DIR = Path(__file__).parent / "kiwinails-website" / "assets" / "images" / "products" / "labels"
LABELS_DIR.mkdir(parents=True, exist_ok=True)

from PIL import Image, ImageFilter

try:
    from rembg import remove, new_session
    REMBG_OK = True
    SESSION = new_session("u2net")
except Exception as exc:  # pragma: no cover
    print(f"rembg unavailable: {exc}")
    REMBG_OK = False
    SESSION = None


def heic_to_jpg(src: Path, tmp: Path) -> bool:
    res = subprocess.run(
        ["sips", "-s", "format", "jpeg", "--resampleHeightWidthMax", "1800",
         str(src), "--out", str(tmp)],
        capture_output=True,
    )
    return res.returncode == 0 and tmp.exists()


def process(src: Path):
    name = src.stem
    out_png = OUT_DIR / f"{name}.png"
    if out_png.exists():
        return f"skip {name}"

    tmp_jpg = OUT_DIR / f"_tmp_{name}.jpg"
    if not heic_to_jpg(src, tmp_jpg):
        return f"FAIL convert {name}"

    img = Image.open(tmp_jpg).convert("RGB")
    w, h = img.size

    # Crop bottom label band (~ bottom 18%) for OCR later
    label_band = img.crop((int(w * 0.15), int(h * 0.78), int(w * 0.85), h))
    label_band.save(LABELS_DIR / f"{name}_label.jpg", quality=80)

    # Crop product region (drop bottom label + top watermark margin)
    prod_crop = img.crop((int(w * 0.05), int(h * 0.05), int(w * 0.95), int(h * 0.78)))

    if REMBG_OK:
        cut = remove(prod_crop, session=SESSION, alpha_matting=False)
    else:
        cut = prod_crop.convert("RGBA")

    # Compose onto soft white background
    bg = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    bg.paste(cut, (0, 0), cut)

    # Resize to consistent width 1500px max
    max_w = 1500
    if bg.size[0] > max_w:
        ratio = max_w / bg.size[0]
        bg = bg.resize((max_w, int(bg.size[1] * ratio)), Image.LANCZOS)

    bg.convert("RGB").save(out_png.with_suffix(".jpg"), quality=88, optimize=True)
    bg.save(out_png, optimize=True)

    tmp_jpg.unlink(missing_ok=True)
    return f"ok   {name}"


def main():
    files = sorted([p for p in SRC.iterdir() if p.suffix.lower() == ".heic"])
    print(f"Found {len(files)} HEIC files")
    for i, p in enumerate(files, 1):
        msg = process(p)
        print(f"[{i:>3}/{len(files)}] {msg}", flush=True)


if __name__ == "__main__":
    main()
