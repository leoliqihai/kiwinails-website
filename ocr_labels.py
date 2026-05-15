"""Run OCR on cropped label images to extract SKU codes and build
a mapping: { SKU: image_filename } so the website can pull the right
photo for each product.

Strategy: the SKU on every label is uppercase letters/digits with dashes
(e.g. RDHP-R31565RV, NDSS-30575R, M565SSDS500). We grab the longest such
token from the OCR output.
"""
import json
import re
import subprocess
from pathlib import Path

LABELS = Path("/Users/yw19990803/Downloads/drive-download-20260512T094550Z-3-001/kiwinails-website/assets/images/products/labels")
OUT = Path("/Users/yw19990803/Downloads/drive-download-20260512T094550Z-3-001/kiwinails-website/js/photo_map.json")
PHOTOS = Path("/Users/yw19990803/Downloads/drive-download-20260512T094550Z-3-001/kiwinails-website/assets/images/products/photos")

TOKEN_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,}[A-Z0-9\-/]{2,}\b")
SIZE_RE = re.compile(r"(\d+\.?\d*\s*[xX×]\s*\d+\.?\d*\s*mm)", re.I)


def ocr(img: Path) -> str:
    res = subprocess.run(
        ["tesseract", str(img), "-", "--psm", "6", "-l", "eng"],
        capture_output=True, text=True,
    )
    return res.stdout


def find_sku(text: str) -> str:
    """Pick the most SKU-like token in the OCR text."""
    text = text.upper()
    # collapse spaces around dashes
    text = re.sub(r"\s*-\s*", "-", text)
    candidates = TOKEN_RE.findall(text)
    # Filter out obvious non-SKU words
    BANNED = {
        "RING", "SMOOTH", "GALV", "HD", "SS304", "SS316", "STEEL", "BRIGHT",
        "ROUND", "FLAT", "HEAD", "PCS/CTN", "PCS", "CTN", "BARCODE", "NAILS",
        "NAIL", "PLYGRIP", "WEATHERBOARD", "COLLATED", "PAPER", "WIRE", "PLASTIC",
        "BOLT", "NUT", "SCREW", "HEX", "STAINLESS", "JOLT", "TYPE", "S/ST",
        "MM", "HOT-DIP", "PAINTED", "BRONZE", "SILICON", "DECKING",
    }
    candidates = [c for c in candidates if c not in BANNED]
    # Heuristic: prefer tokens with a dash (most SKUs have one)
    dashed = [c for c in candidates if "-" in c]
    pool = dashed if dashed else candidates
    if not pool:
        return ""
    # Prefer the longest token (most info-rich)
    pool.sort(key=lambda s: (-len(s), s))
    return pool[0]


def main():
    label_files = sorted(LABELS.glob("*_label.jpg"))
    print(f"Found {len(label_files)} labels")

    mapping = {}
    raw_log = []
    for i, lp in enumerate(label_files, 1):
        text = ocr(lp)
        sku = find_sku(text)
        photo_name = lp.stem.replace("_label", "")
        # only keep mapping if photo actually exists
        if not (PHOTOS / f"{photo_name}.jpg").exists():
            continue
        raw_log.append({"photo": photo_name, "sku_guess": sku, "raw": text.strip()})
        if sku:
            # If multiple photos map to same SKU, keep the first (or could collect a list)
            mapping.setdefault(sku, []).append(photo_name)
        if i % 20 == 0:
            print(f"  {i}/{len(label_files)} processed")

    OUT.parent.mkdir(exist_ok=True, parents=True)
    OUT.write_text(json.dumps(mapping, indent=2))
    (OUT.parent / "photo_map_raw.json").write_text(json.dumps(raw_log, indent=2))
    print(f"Wrote {OUT} ({len(mapping)} unique SKUs)")
    print(f"Wrote raw OCR log for manual review")


if __name__ == "__main__":
    main()
