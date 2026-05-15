"""Parse the Kiwi Nails Excel into a structured product catalog JSON.

Strategy: each sheet contains multiple sub-tables. Each sub-table is preceded
by a 'section header' row (single non-empty cell in column B, no other data),
then a column-header row (Size, Material, ..., Product Code, Barcode, Price...),
then product data rows.
"""
import json
import re
from pathlib import Path

import openpyxl

ROOT = Path(__file__).parent
SRC = ROOT / "Kiwi-Nails-List-2026-MAY.xlsx"
OUT = ROOT / "kiwinails-website" / "js" / "products.json"


# Category metadata: sheet -> category id + display name + image color
CATEGORY_META = {
    "Hardware": {
        "id": "hardware",
        "name": "Hardware & Brackets",
        "blurb": "Construction-grade hardware: brace straps, joist hangers, washers, soakers and pin anchors.",
    },
    "screws": {
        "id": "screws",
        "name": "Screws",
        "blurb": "Decking, batten, chipboard, purlin, jolt-head and HWF/Tek screws in stainless and Ruspert coated.",
    },
    "Gun nails": {
        "id": "collated-nails",
        "name": "Collated Gun Nails",
        "blurb": "34° paper-collated framing, weatherboard and joist-hanger nails plus brads & staples.",
    },
    "Coil": {
        "id": "coil-nails",
        "name": "Coil Nails",
        "blurb": "Plastic and wire collated coil nails for siding, fencing, roofing and industrial use.",
    },
    "Bolts": {
        "id": "bolts",
        "name": "Bolts & Anchors",
        "blurb": "Engineering bolts, coach bolts, screw bolts, through bolts and coach screws.",
    },
    "Loose Nails": {
        "id": "loose-nails",
        "name": "Loose Nails",
        "blurb": "Bright, HD galvanised, stainless and silicon bronze loose nails for trade and retail.",
    },
}


HEADER_TOKENS = {
    "size",
    "material",
    "head",
    "drive",
    "pack",
    "pack size",
    "product code",
    "barcode",
    "price",
    "shank",
    "fuel cell",
    "collation",
    "price/pcs",
    "price/pack",
}


def is_header_row(row):
    nonempty = [str(c).strip().lower() for c in row if c and str(c).strip()]
    if not nonempty:
        return False
    # at least 3 known header tokens means this is a column header row
    hits = sum(1 for t in nonempty if any(t.startswith(h) for h in HEADER_TOKENS))
    return hits >= 3


def is_section_header(row):
    """A section header is a row with exactly one non-empty cell that does NOT look like data."""
    non_empty = [(i, str(c).strip()) for i, c in enumerate(row) if c is not None and str(c).strip()]
    if len(non_empty) != 1:
        return False
    text = non_empty[0][1]
    # data rows always start with size or numeric, headers tend to be descriptive
    if re.search(r"\d+\s*[xX×]\s*\d+", text):
        return False
    if text.lower() in HEADER_TOKENS:
        return False
    return True


def normalize_header(row):
    return [str(c).strip() if c else "" for c in row]


def slug(text):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return s or "x"


def clean(v):
    if v is None:
        return ""
    s = str(v).replace("\xa0", " ").strip()
    return s


def parse_sheet(ws, category):
    sections = []  # list of {title, items: [...]}
    current_section = None
    current_headers = None
    last_size = ""  # for rows where 'Size' is blank (continuation)
    last_material = ""

    rows = list(ws.iter_rows(values_only=True))
    for row in rows:
        # strip leading None column (the first column is always blank)
        row = list(row)
        if not any(c is not None and str(c).strip() for c in row):
            continue

        if is_section_header(row):
            title = next(str(c).strip() for c in row if c)
            current_section = {"title": title, "items": []}
            sections.append(current_section)
            current_headers = None
            last_size = last_material = ""
            continue

        if is_header_row(row):
            current_headers = normalize_header(row)
            continue

        if current_section is None or current_headers is None:
            continue  # data row outside any known section, skip

        # data row — map by header
        item = {}
        for i, header in enumerate(current_headers):
            if not header:
                continue
            v = clean(row[i]) if i < len(row) else ""
            item[header] = v

        # carry-down for blank size / material rows
        size = item.get("Size", "") or last_size
        material = item.get("Material", "") or last_material
        if item.get("Size"):
            last_size = item["Size"]
        if item.get("Material"):
            last_material = item["Material"]
        item["Size"] = size
        item["Material"] = material

        # Skip if no product code
        code = item.get("Product Code", "")
        if not code:
            continue

        item["sku"] = code
        item["slug"] = slug(code)
        current_section["items"].append(item)

    return sections


def main():
    wb = openpyxl.load_workbook(SRC, data_only=True)

    catalog = {"categories": []}
    for sheet_name, meta in CATEGORY_META.items():
        ws = wb[sheet_name]
        sections = parse_sheet(ws, meta)
        # total products
        total = sum(len(s["items"]) for s in sections)
        catalog["categories"].append(
            {
                "id": meta["id"],
                "name": meta["name"],
                "blurb": meta["blurb"],
                "sheet": sheet_name,
                "total_skus": total,
                "sections": sections,
            }
        )
        print(f"  {sheet_name:>14} -> {total} SKUs in {len(sections)} sections")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    total = sum(c["total_skus"] for c in catalog["categories"])
    print(f"\nTotal SKUs: {total}")
    print(f"Written: {OUT}")


if __name__ == "__main__":
    main()
