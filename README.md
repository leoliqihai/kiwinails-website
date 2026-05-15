# Kiwi Nails Fasteners Ltd — Website (v2)

A photo-first, **display-only** website for Kiwi Nails Fasteners Ltd (East Tamaki, Auckland).
This is **not** an e-commerce site. There are no prices anywhere — pricing is provided
to trade customers on request.

> Director: **Linda Kong** · Issue: May 2026 · v2.0

---

## What's new in v2

| Area | Change |
| --- | --- |
| **Logo** | Real logo extracted from your official 2020 product catalogue (PDF page 1). No more SVG approximation. |
| **Brand colours** | Navy `#1f3a6b` + Orange `#E87722`, matching the catalogue tables and headings. |
| **Product images** | Your real green-screen photos cut out + AI-enhanced via OpenAI `gpt-image-1` **image-edit** endpoint at **high quality** — proper studio lighting, shadows, sharpness preserved per product family. 31 unique enhanced photos cover the OCR-matched bestseller SKUs. Remaining SKUs use AI-generated category heroes (59 of them, also `gpt-image-1`). All HD quality. |
| **Layout** | Photo-first bento grid. Home → Category → **Sub-category** (new tier) → individual SKU. Click any photo to drill down. |
| **No prices** | Every price column / hero stat / catalogue page has prices removed. Replaced with "Request quote" CTAs. |
| **Certifications** | Dedicated `/certifications.html` page prominently showing the two BRANZ Appraisals (No. 1132 Joist Hangers, No. 1133 CPCs — both issued 25 Nov 2025), the BRANZ Standards Test ST1224 for the 90×3.15mm bright framing nail, and the ISO 9001 manufacturing certification. Also a cert strip on home page under the hero. |
| **Content** | About / Manufacturing / Why us / Logistics text rewritten from your official PDF copy (not invented). |
| **Address** | East Tamaki, Auckland throughout (was just "Auckland"). |
| **Accessibility** | 4.5:1 contrast, focus-visible outlines, `prefers-reduced-motion` respected, all icons are SVG (Lucide-style) — no emoji per UI/UX guidelines. |

---

## Folder layout

```
kiwinails-website/
├── index.html                Hero + categories + Why us + Manufacturing + Logistics + CTA
├── products.html             6 category bento grid
├── certifications.html       ★ BRANZ Appraisals + ISO 9001
├── about.html                Company story + manufacturing + Why us bullets
├── trade.html                Trade account application
├── contact.html              Contact form + East Tamaki details
├── downloads.html            Catalogues + BPIR + compliance docs
│
├── category/                 6 category pages
│   ├── loose-nails.html
│   ├── loose-nails/          ↓ sub-category drill-down pages (29 for loose nails alone)
│   │   ├── flat-head-nails-hd-galv.html
│   │   ├── jolt-head-nails-stainless-steel-316.html
│   │   └── … etc
│   └── … (same pattern for other 5 categories)
│
├── products/                 412 individual product pages
├── catalogs/                 6 printable per-category catalogues (⌘P to PDF)
├── docs/                     BPIR · Material compliance · Barcode statement (all for Linda to print/sign)
│
├── assets/images/
│   ├── site/
│   │   ├── logo.png          ★ Real logo extracted from PDF
│   │   ├── favicon.png
│   │   └── hero/             59 AI-generated product photos
│   └── products/
│       ├── photos/           193 processed photos from your green-screen shoot
│       └── labels/           Original label crops (for SKU verification)
│
├── css/styles.css            v2 stylesheet (navy + orange palette)
└── js/
    ├── products.json         Source-of-truth catalogue (parsed from your Excel)
    └── photo_map.json        SKU → real-photo mapping (OCR-driven)
```

---

## Linda's go-live checklist

1. **Confirm the NZBN** — currently `[to be inserted before issue]` in:
   - `docs/bpir-declaration.html` § 1. Manufacturer
2. **Confirm contact details** — update at the top of `build_site.py` if any of these are wrong:
   - Phone: `+64 9 887 1230`
   - Email: `sales@kiwinails.co.nz`
   - Address: `East Tamaki · Auckland, New Zealand`
   - Director: `Linda Kong`
3. **Sign the BPIR**:
   - Open `docs/bpir-declaration.html` in any browser → Print (⌘P) → Save as PDF.
   - Sign the PDF (Preview Markup or print + wet sign).
   - Save the signed PDF back as `docs/bpir-declaration.pdf`.
4. **Trade page form / Contact form**:
   - Currently the forms show a JS alert on submit. For real submissions: drop the site on Netlify and add `netlify` to each `<form>` tag — Netlify Forms is free up to 100 submissions/month and emails them to you.

---

## Editing the site

Everything regenerates from one script:

```bash
python3 parse_excel.py        # Excel → products.json (run if Excel changes)
python3 gen_images.py         # generates any missing AI product images (rate-limited)
python3 ocr_labels.py         # re-maps any new green-screen photos to SKUs
python3 build_site.py         # rebuilds all HTML pages
```

To change page copy (About text, Why-us bullets, BPIR sections, etc.) → edit the
`render_<page>()` function in `build_site.py` and re-run it.

---

## Deploying

The site is pure static HTML/CSS — no server runtime needed. Easiest options:

### Option A — Netlify (recommended, free)
1. Open https://app.netlify.com → drag-and-drop the entire `kiwinails-website/` folder.
2. Netlify gives you a `*.netlify.app` URL within 30 seconds.
3. Add the custom domain via **Domain settings → Add custom domain** and follow the DNS hints.
4. To make the forms actually work, add `netlify` to every `<form>` tag in `build_site.py` and re-run.

### Option B — Cloudflare Pages (free, faster in NZ)
1. Push `kiwinails-website/` to a GitHub repo.
2. Cloudflare Pages → Connect to Git → Output dir: `/`. No build command needed.

### Option C — Your own web host
Upload the entire `kiwinails-website/` folder to your hosting account's `public_html`.

---

## References

- Brand assets and copy taken from your official **KBAOProductCatalogue.pdf** (v02, Aug 2020).
- Comparable sites studied: ecko.co.nz, hitools.co.nz/shop/category/shop-by-brand/kiwinail/, jafasteners.co.nz/kiwi-nails.
- UI/UX principles applied from the `nextlevelbuilder/ui-ux-pro-max-skill` repo (responsive 375/768/1024/1440, focus-visible, prefers-reduced-motion, SVG icons over emoji, 4.5:1 contrast).
- Category heroes generated via OpenAI `gpt-image-1` (1024×1024, **high quality**) using your API key. Individual product photos are your own green-screen shots, polished via `gpt-image-1` **image-edit** endpoint — original product preserved, only lighting/shadow/background improved. The key is stored in a `.env` file (chmod 600) and listed in `.gitignore` — **never** committed to source.

— Built for Linda Kong, Director — Kiwi Nails Fasteners Ltd, East Tamaki, Auckland
