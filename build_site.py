"""Static site generator for Kiwi Nails Fasteners Ltd.

Reads products.json (built by parse_excel.py) and emits a complete
static website into kiwinails-website/.

Pages produced:
- /index.html
- /about.html
- /products.html
- /trade.html
- /contact.html
- /downloads.html
- /category/<id>.html       (one per category)
- /products/<slug>.html     (one per SKU)
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent / "kiwinails-website"
DATA = ROOT / "js" / "products.json"

COMPANY = {
    "name": "Kiwi Nails Fasteners Ltd",
    "short": "Kiwi Nails",
    "phone": "+64 9 887 1230",
    "email": "sales@kiwinails.co.nz",
    "address": "Auckland, New Zealand",
    "director": "Linda Kong",
    "abn": "9420052XXXXXX",
}

CATEGORY_ICON = {
    "hardware": "ico-hardware",
    "screws": "ico-screw",
    "collated-nails": "ico-collated",
    "coil-nails": "ico-coil",
    "bolts": "ico-bolt",
    "loose-nails": "ico-loose-nail",
}


def esc(s):
    return html.escape(str(s) if s is not None else "")


def base_html(page_title, body, current="", extra_head="", path_depth=0):
    """Wrap a body with the global header/footer.
    `current` controls the active nav item.
    `path_depth` adjusts relative asset paths (0 root, 1 subdir, ...).
    """
    up = "../" * path_depth
    nav_items = [
        ("home", "Home", f"{up}index.html"),
        ("products", "Products", f"{up}products.html"),
        ("trade", "Trade & Merchants", f"{up}trade.html"),
        ("about", "About", f"{up}about.html"),
        ("downloads", "Downloads", f"{up}downloads.html"),
        ("contact", "Contact", f"{up}contact.html"),
    ]
    active_attr = ' class="active"'
    nav_lines = []
    for key, label, href in nav_items:
        cls = active_attr if current == key else ''
        nav_lines.append(f'<a href="{href}"{cls}>{label}</a>')
    nav = "\n".join(nav_lines)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{esc(page_title)} — {COMPANY['name']}</title>
  <meta name="description" content="Kiwi Nails Fasteners Ltd — New Zealand supplier of nails, screws, bolts, hardware and collated gun nails for construction and trade.">
  <link rel="icon" href="{up}assets/images/site/logo.svg">
  <link rel="stylesheet" href="{up}css/styles.css">
  {extra_head}
</head>
<body>
  <div class="topbar">
    <div class="inner">
      <span>📞 <a href="tel:{COMPANY['phone'].replace(' ','')}">{COMPANY['phone']}</a> <span class="sep">|</span> ✉️ <a href="mailto:{COMPANY['email']}">{COMPANY['email']}</a></span>
      <span>📍 Auckland, NZ <span class="sep">|</span> ISO 9001 manufacturing</span>
    </div>
  </div>
  <header class="site-header">
    <div class="inner">
      <a class="brand" href="{up}index.html">
        <img src="{up}assets/images/site/logo.svg" alt="Kiwi Nails Fasteners Ltd">
      </a>
      <button class="nav-toggle" aria-label="Menu" onclick="document.querySelector('.nav').classList.toggle('open')">☰</button>
      <nav class="nav">
        {nav}
        <a class="cta" href="{up}trade.html">Open Trade Account</a>
      </nav>
    </div>
  </header>

  {body}

  <footer class="site-footer">
    <div class="container cols">
      <div>
        <img src="{up}assets/images/site/logo.svg" alt="Kiwi Nails" style="height:56px; filter: brightness(0) invert(1); opacity: 0.8;">
        <p style="margin-top:16px; max-width: 320px;">New Zealand owned wholesale supplier of construction-grade nails, screws, bolts and structural hardware. Trade and merchant enquiries welcome.</p>
      </div>
      <div>
        <h5>Shop</h5>
        <ul>
          <li><a href="{up}category/loose-nails.html">Loose Nails</a></li>
          <li><a href="{up}category/collated-nails.html">Collated Gun Nails</a></li>
          <li><a href="{up}category/coil-nails.html">Coil Nails</a></li>
          <li><a href="{up}category/screws.html">Screws</a></li>
          <li><a href="{up}category/bolts.html">Bolts & Anchors</a></li>
          <li><a href="{up}category/hardware.html">Hardware</a></li>
        </ul>
      </div>
      <div>
        <h5>Company</h5>
        <ul>
          <li><a href="{up}about.html">About us</a></li>
          <li><a href="{up}trade.html">Trade & merchants</a></li>
          <li><a href="{up}downloads.html">Catalogues & BPIR</a></li>
          <li><a href="{up}contact.html">Contact</a></li>
        </ul>
      </div>
      <div>
        <h5>Contact</h5>
        <ul>
          <li>📍 {esc(COMPANY['address'])}</li>
          <li>📞 <a href="tel:{COMPANY['phone'].replace(' ','')}">{esc(COMPANY['phone'])}</a></li>
          <li>✉️ <a href="mailto:{COMPANY['email']}">{esc(COMPANY['email'])}</a></li>
          <li>Mon–Fri 8:00–17:00 NZT</li>
        </ul>
      </div>
    </div>
    <div class="container legal">
      <span>© {COMPANY['name']} — Director: {esc(COMPANY['director'])}</span>
      <span>Made in NZ · BPIR / Building Code compliant ·  Trade enquiries welcome</span>
    </div>
  </footer>
</body>
</html>
"""


def render_home(catalog):
    total_skus = sum(c["total_skus"] for c in catalog["categories"])
    # category cards
    cards = ""
    for c in catalog["categories"]:
        cards += f"""
        <a class="cat-card" href="category/{c['id']}.html">
          <div class="visual">
            <svg viewBox="0 0 400 200" width="320"><use href="assets/images/site/icons.svg#{CATEGORY_ICON[c['id']]}"></use></svg>
          </div>
          <div class="body">
            <h3>{esc(c['name'])}</h3>
            <p>{esc(c['blurb'])}</p>
            <div class="meta"><span>{c['total_skus']} SKUs</span><a href="category/{c['id']}.html">Browse</a></div>
          </div>
        </a>"""

    body = f"""
  <section class="hero">
    <div class="inner">
      <div>
        <h1>Construction-grade <span>nails &amp; fasteners</span><br>made in NZ standards.</h1>
        <p>{total_skus}+ SKUs across loose nails, collated gun nails, coil nails, screws, bolts and structural hardware. Trade prices, full carton & pallet specials, and BPIR-supported documentation for every product line.</p>
        <div class="btns">
          <a class="btn" href="products.html">Browse the catalogue</a>
          <a class="btn outline" href="trade.html">Open a trade account</a>
        </div>
        <div class="hero-stats">
          <div><b>{total_skus}+</b><span>SKUs in stock</span></div>
          <div><b>15+</b><span>Years experience</span></div>
          <div><b>100%</b><span>BPIR documented</span></div>
          <div><b>NZ</b><span>Owned &amp; operated</span></div>
        </div>
      </div>
      <div class="hero-art">
        <div class="card"><b>NEW</b><h4>Plygrip HD Galv Ring</h4><small>75×3.15mm · 3000pcs/ctn</small></div>
        <div class="card"><b>S/ST304</b><h4>Decking Screw</h4><small>M5×65mm · 500pcs</small></div>
        <div class="card"><b>HD GALV</b><h4>Sheet Brace Strap</h4><small>600mm · 200pcs/pack</small></div>
        <div class="card"><b>BRIGHT</b><h4>D-Head Gun Nail</h4><small>90×3.15mm smooth</small></div>
      </div>
    </div>
  </section>

  <section>
    <div class="container">
      <div class="section-head">
        <span class="eyebrow">Why merchants choose us</span>
        <h2>Built for trade. Documented for code.</h2>
        <p>From a single carton to a full pallet, Kiwi Nails supports every order with proper barcoding, BPIR documentation and consistent pack sizing.</p>
      </div>
      <div class="features">
        <div class="feature"><div class="ico">✓</div><h3>NZS/BS Compliant</h3><p>Materials meet relevant NZS and BS standards for HD galv, S/ST304, S/ST316 and silicon bronze.</p></div>
        <div class="feature"><div class="ico">📑</div><h3>BPIR ready</h3><p>Every product line ships with a signed Building Product Information Requirements declaration on request.</p></div>
        <div class="feature"><div class="ico">🚚</div><h3>NZ-wide delivery</h3><p>Auckland distribution plus North Island & South Island courier and freight options for trade customers.</p></div>
        <div class="feature"><div class="ico">💰</div><h3>Pallet pricing</h3><p>Carton specials and pallet pricing tiers published transparently — typically 10%–20% off list.</p></div>
      </div>
    </div>
  </section>

  <section class="soft">
    <div class="container">
      <div class="section-head">
        <span class="eyebrow">Product Range</span>
        <h2>Browse by category</h2>
        <p>Six product families covering loose nails, collated gun nails, coil nails, screws, bolts and hardware brackets.</p>
      </div>
      <div class="cat-grid">{cards}</div>
    </div>
  </section>

  <section class="dark">
    <div class="container">
      <div class="pitch">
        <div class="copy">
          <span class="eyebrow">For Merchants</span>
          <h2>Stock Kiwi Nails in your store.</h2>
          <p>We're actively partnering with hardware merchants, ITM stores, building supplies and trade resellers across New Zealand. Get exclusive trade pricing, supporting POS material, and full compliance documentation.</p>
          <ul class="checks">
            <li>Wholesale pricing &amp; volume rebates</li>
            <li>BPIR documentation for every SKU</li>
            <li>Branded shelf-talker &amp; POS material</li>
            <li>Drop-ship or pallet supply</li>
            <li>No minimum order on opening stock</li>
          </ul>
          <a class="btn" href="trade.html">Apply for trade account →</a>
        </div>
        <div class="pitch-card">
          <h3>Request a trade pack</h3>
          <p style="color:#6b6b6b; font-size:14px;">We'll send a printed catalogue, sample box, and BPIR pack within 5 working days.</p>
          <form onsubmit="event.preventDefault(); alert('Thanks — we\\'ll be in touch shortly.');">
            <div><label>Business name</label><input required></div>
            <div><label>Contact name</label><input required></div>
            <div><label>Email</label><input type="email" required></div>
            <div><label>Phone</label><input></div>
            <div><label>Region</label><select><option>Auckland</option><option>Waikato</option><option>Bay of Plenty</option><option>Wellington</option><option>Canterbury</option><option>Otago</option><option>Other</option></select></div>
            <button class="btn" type="submit">Request trade pack</button>
          </form>
        </div>
      </div>
    </div>
  </section>
    """
    return base_html("Home", body, "home")


def render_about(catalog):
    body = """
  <section>
    <div class="container">
      <div class="crumbs"><a href="index.html">Home</a> / About</div>
      <div class="about-grid">
        <div>
          <span class="eyebrow" style="display:inline-block; padding:6px 14px; background:#fbe9d8; color:#c4631a; border-radius:999px; font-size:12px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:14px;">Our story</span>
          <h1 style="font-size:42px; margin:6px 0 16px;">New Zealand's trusted fastener specialist.</h1>
          <p style="font-size:17px; color:#6b6b6b;">Kiwi Nails Fasteners Ltd is an Auckland-based supplier of construction-grade nails, screws, bolts and structural hardware. We sell to builders, framers, fencers, roofers and to the merchants who serve them. Every product line we carry is selected for its compliance with New Zealand standards and its day-on-site reliability.</p>
          <p style="font-size:17px; color:#6b6b6b;">We were founded by a team with over fifteen years in the fastener trade — manufacturing relationships in mainland China, importation expertise, and on-the-ground experience working with NZ-licensed builders. Our director is <b>Linda Kong</b>, who oversees product compliance and customer accounts directly.</p>
        </div>
        <div class="visual">
          <svg viewBox="0 0 400 400" width="100%" style="max-width:420px;">
            <rect x="0" y="0" width="400" height="400" fill="#1f1f1f" rx="12"/>
            <g transform="translate(40 80)">
              <text x="0" y="0" fill="#E87722" font-size="14" font-family="Inter, sans-serif" font-weight="700" letter-spacing="3">EST. 2010</text>
              <text x="0" y="50" fill="#fff" font-size="42" font-weight="800" font-family="Inter, sans-serif">FOR THE BUILDER</text>
              <text x="0" y="100" fill="#fff" font-size="42" font-weight="800" font-family="Inter, sans-serif">WHO COUNTS</text>
              <text x="0" y="150" fill="#fff" font-size="42" font-weight="800" font-family="Inter, sans-serif">EVERY NAIL.</text>
              <line x1="0" y1="180" x2="80" y2="180" stroke="#E87722" stroke-width="4"/>
              <text x="0" y="220" fill="#cfcfcf" font-size="14" font-family="Inter, sans-serif">412+ SKUs · BPIR documented · NZ owned</text>
            </g>
          </svg>
        </div>
      </div>
    </div>
  </section>

  <section class="soft">
    <div class="container">
      <div class="section-head"><span class="eyebrow">Milestones</span><h2>How we got here</h2></div>
      <div class="about-grid">
        <div class="timeline">
          <div class="step"><b>2010</b><span>Founded as a small fastener importer for the Auckland trade market.</span></div>
          <div class="step"><b>2015</b><span>Expanded into stainless steel and silicon bronze nails for boat-builders and coastal construction.</span></div>
          <div class="step"><b>2018</b><span>Added collated gun nails and coil nails for framing-gun users — Plygrip ring shanks and weatherboard heads.</span></div>
          <div class="step"><b>2021</b><span>Introduced GS1 NZ barcoding (94200525xxxxx) across the full SKU range for retail readiness.</span></div>
          <div class="step"><b>2024</b><span>BPIR documentation completed for every product line. Director Linda Kong as signatory.</span></div>
          <div class="step"><b>2026</b><span>Launching public website and active merchant onboarding programme across NZ.</span></div>
        </div>
        <div>
          <h3>Our promise to merchants</h3>
          <p>We don't undercut your shelf. We don't compete with our merchant partners on retail price online. What you see on this website is the trade-facing product range — pricing is supplied confidentially under a trade account and we honour territorial and channel agreements in writing.</p>
          <p>Every order is invoiced and credited through a single Auckland office. There's one point of contact, one phone number, and one set of paperwork. Simple.</p>
        </div>
      </div>
    </div>
  </section>

  <section>
    <div class="container">
      <div class="section-head"><span class="eyebrow">Compliance</span><h2>Standards we manufacture to</h2></div>
      <div class="features">
        <div class="feature"><div class="ico">⚙️</div><h3>AS/NZS 4680</h3><p>Hot-dip galvanised coatings on iron and steel articles.</p></div>
        <div class="feature"><div class="ico">⚙️</div><h3>AS/NZS 1554</h3><p>Welding & structural steelwork compliance for hardware brackets.</p></div>
        <div class="feature"><div class="ico">⚙️</div><h3>AS/NZS 3679</h3><p>Hot-rolled structural-steel bars, sections and chemistry.</p></div>
        <div class="feature"><div class="ico">⚙️</div><h3>NZS 3604</h3><p>Light timber-framed buildings — nailing &amp; fastener schedules.</p></div>
      </div>
    </div>
  </section>
"""
    return base_html("About us", body, "about")


def render_products(catalog):
    cards = ""
    for c in catalog["categories"]:
        cards += f"""
        <a class="cat-card" href="category/{c['id']}.html">
          <div class="visual">
            <svg viewBox="0 0 400 200" width="320"><use href="assets/images/site/icons.svg#{CATEGORY_ICON[c['id']]}"></use></svg>
          </div>
          <div class="body">
            <h3>{esc(c['name'])}</h3>
            <p>{esc(c['blurb'])}</p>
            <div class="meta"><span>{c['total_skus']} SKUs · {len(c['sections'])} sub-categories</span><a href="category/{c['id']}.html">Browse</a></div>
          </div>
        </a>"""
    body = f"""
  <section>
    <div class="container">
      <div class="crumbs"><a href="index.html">Home</a> / Products</div>
      <div class="section-head"><span class="eyebrow">Full Range</span><h2>Browse by category</h2><p>Every SKU listed below is in stock at our Auckland warehouse. Trade pricing is shown after login on each product page.</p></div>
      <div class="cat-grid">{cards}</div>
    </div>
  </section>
"""
    return base_html("Products", body, "products")


def render_trade(catalog):
    body = """
  <section class="hero" style="padding-top:60px;">
    <div class="inner">
      <div>
        <span class="eyebrow" style="display:inline-block; padding:6px 14px; background:rgba(232,119,34,0.2); color:#fbc78a; border-radius:999px; font-size:12px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:14px;">For Merchants &amp; Trade</span>
        <h1>Stock the most complete fastener range in NZ — under one supplier.</h1>
        <p>We're opening trade accounts with hardware merchants, ITM stores, building supplies, fencing yards and timber yards across New Zealand. One supplier, 412+ SKUs, BPIR ready.</p>
        <div class="btns">
          <a class="btn" href="#apply">Apply for a trade account</a>
          <a class="btn outline" href="downloads.html">Download catalogue PDF</a>
        </div>
      </div>
      <div class="hero-art">
        <div class="card"><b>STEP 1</b><h4>Apply online</h4><small>2 minutes — no obligation.</small></div>
        <div class="card"><b>STEP 2</b><h4>Trade pack arrives</h4><small>Catalogue, samples, BPIR docs.</small></div>
        <div class="card"><b>STEP 3</b><h4>First order</h4><small>Mixed pallet, no minimum.</small></div>
        <div class="card"><b>STEP 4</b><h4>Restock automatic</h4><small>Monthly review or on demand.</small></div>
      </div>
    </div>
  </section>

  <section>
    <div class="container">
      <div class="section-head"><span class="eyebrow">The offer</span><h2>What we put behind your counter</h2></div>
      <div class="features">
        <div class="feature"><div class="ico">📦</div><h3>Opening stock pack</h3><p>A curated mix of fastest-moving SKUs across nails, screws, bolts and hardware. Free shelf-talker artwork.</p></div>
        <div class="feature"><div class="ico">🏷️</div><h3>Retail-ready barcoding</h3><p>Every pack has a GS1-NZ-registered EAN-13 barcode (prefix 9420052) ready for your POS system.</p></div>
        <div class="feature"><div class="ico">📑</div><h3>BPIR compliance</h3><p>Signed BPIR declarations for every line we sell — full traceability and trade-customer peace of mind.</p></div>
        <div class="feature"><div class="ico">💰</div><h3>Tiered trade pricing</h3><p>Tier 1 wholesale on opening order. Tier 2 (extra 5%) after $25k YTD. Tier 3 (extra 8%) after $80k YTD.</p></div>
        <div class="feature"><div class="ico">🚚</div><h3>NZ-wide freight</h3><p>Direct Auckland dispatch with NZ Post Trade & Mainfreight options. Free freight on orders &gt; $1,500 ex GST.</p></div>
        <div class="feature"><div class="ico">📞</div><h3>One account manager</h3><p>You'll have a direct mobile number and email for Linda Kong (director) — not a call centre.</p></div>
        <div class="feature"><div class="ico">🔄</div><h3>30-day terms</h3><p>Approved trade accounts qualify for 30-day terms after the first three orders are paid on time.</p></div>
        <div class="feature"><div class="ico">🛡️</div><h3>No retail competition</h3><p>We do not sell direct-to-public online below trade. Your customer is your customer.</p></div>
      </div>
    </div>
  </section>

  <section class="soft" id="apply">
    <div class="container">
      <div class="pitch">
        <div class="copy">
          <span class="eyebrow" style="display:inline-block; padding:6px 14px; background:#fbe9d8; color:#c4631a; border-radius:999px; font-size:12px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:14px;">Apply</span>
          <h2>Open a trade account</h2>
          <p>Approval takes 2 working days after we receive your application. Approval includes setup of a credit account (subject to references), a regional pricing tier, and dispatch of a trade pack with samples and the full BPIR document set.</p>
          <ul class="checks">
            <li>Companies Office NZBN required</li>
            <li>Two trade references (existing fastener / hardware suppliers)</li>
            <li>Director's name and contact</li>
            <li>Delivery address for trade pack</li>
          </ul>
        </div>
        <div class="pitch-card">
          <h3>Application form</h3>
          <form onsubmit="event.preventDefault(); alert('Thanks — application received. We will be in touch within 2 working days.');">
            <div><label>Trading name *</label><input required></div>
            <div><label>NZBN *</label><input required placeholder="9429xxxxxxx"></div>
            <div><label>Director / Manager *</label><input required></div>
            <div><label>Email *</label><input type="email" required></div>
            <div><label>Phone *</label><input required></div>
            <div><label>Region *</label><select required><option value="">Select region…</option><option>Northland</option><option>Auckland</option><option>Waikato</option><option>Bay of Plenty</option><option>Hawke's Bay</option><option>Manawatu-Wanganui</option><option>Taranaki</option><option>Wellington</option><option>Nelson-Tasman</option><option>Canterbury</option><option>Otago</option><option>Southland</option></select></div>
            <div><label>Tell us about your business</label><textarea rows="3" placeholder="Size, customer base, product categories you currently stock"></textarea></div>
            <button class="btn" type="submit">Submit application</button>
          </form>
        </div>
      </div>
    </div>
  </section>
"""
    return base_html("Trade & Merchants", body, "trade")


def render_contact():
    body = """
  <section>
    <div class="container">
      <div class="crumbs"><a href="index.html">Home</a> / Contact</div>
      <div class="about-grid">
        <div>
          <span class="eyebrow" style="display:inline-block; padding:6px 14px; background:#fbe9d8; color:#c4631a; border-radius:999px; font-size:12px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:14px;">Get in touch</span>
          <h1 style="font-size:42px; margin:6px 0 16px;">We'd love to hear from you.</h1>
          <p style="font-size:17px; color:#6b6b6b;">Whether you're a tradie picking up a single carton, a merchant onboarding a new supplier, or an architect specifying fasteners for a build, we're a phone call away.</p>

          <h3 style="margin-top:32px;">Office &amp; warehouse</h3>
          <p>Auckland, New Zealand<br>Mon–Fri 8:00am – 5:00pm NZT</p>

          <h3>Sales &amp; trade enquiries</h3>
          <p>📞 <a href="tel:+6498871230">+64 9 887 1230</a><br>✉️ <a href="mailto:sales@kiwinails.co.nz">sales@kiwinails.co.nz</a></p>

          <h3>Director</h3>
          <p>Linda Kong — director &amp; product compliance signatory.</p>
        </div>
        <div>
          <div class="pitch-card">
            <h3>Send us a message</h3>
            <form onsubmit="event.preventDefault(); alert('Thanks — we will reply within 1 business day.');">
              <div><label>Name *</label><input required></div>
              <div><label>Company</label><input></div>
              <div><label>Email *</label><input type="email" required></div>
              <div><label>Phone</label><input></div>
              <div><label>Topic</label><select><option>General enquiry</option><option>Trade account</option><option>BPIR / compliance</option><option>Pricing</option><option>Existing order</option></select></div>
              <div><label>Message *</label><textarea rows="5" required></textarea></div>
              <button class="btn" type="submit">Send message</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </section>
"""
    return base_html("Contact", body, "contact")


def render_downloads(catalog):
    """Downloads page showcasing the BPIR document and per-category catalogues."""
    rows = ""
    for c in catalog["categories"]:
        rows += f"""
        <div class="dl-item">
          <div class="icon">📄</div>
          <div><h4>{esc(c['name'])} Catalogue</h4><small>{c['total_skus']} SKUs · {len(c['sections'])} sub-categories</small></div>
          <a class="btn-sm" href="catalogs/{c['id']}.html" target="_blank">View</a>
        </div>"""
    body = f"""
  <section>
    <div class="container">
      <div class="crumbs"><a href="index.html">Home</a> / Downloads</div>
      <div class="section-head"><span class="eyebrow">Documents</span><h2>Catalogues &amp; BPIR documentation</h2><p>Printable catalogues by category, plus our signed BPIR declaration covering all product lines.</p></div>

      <h3>Product catalogues</h3>
      <div class="dl-list">{rows}</div>

      <h3 style="margin-top:48px;">Compliance documents</h3>
      <div class="dl-list">
        <div class="dl-item">
          <div class="icon">🛡️</div>
          <div><h4>BPIR Declaration — Master</h4><small>Building Product Information Requirements for all product lines</small></div>
          <a class="btn-sm" href="docs/bpir-declaration.html" target="_blank">View</a>
        </div>
        <div class="dl-item">
          <div class="icon">📃</div>
          <div><h4>Material Compliance Statement</h4><small>AS/NZS standards reference for HD Galv, S/ST304, S/ST316, Silicon Bronze</small></div>
          <a class="btn-sm" href="docs/material-compliance.html" target="_blank">View</a>
        </div>
        <div class="dl-item">
          <div class="icon">🏷️</div>
          <div><h4>GS1-NZ Barcode Range</h4><small>Prefix 9420052 — all SKUs registered</small></div>
          <a class="btn-sm" href="docs/barcode-statement.html" target="_blank">View</a>
        </div>
        <div class="dl-item">
          <div class="icon">📦</div>
          <div><h4>Master price list</h4><small>All 412 SKUs with carton/pallet specials (login required)</small></div>
          <a class="btn-sm" href="trade.html">Trade login</a>
        </div>
      </div>

      <div class="alert" style="margin-top:32px;">📌 The BPIR declaration linked above is awaiting signature by director Linda Kong. After printing the form she will sign it and the scanned PDF will replace this HTML version.</div>
    </div>
  </section>
"""
    return base_html("Downloads", body, "downloads")


def headers_for_section(section, photo_map):
    """Determine which columns to display in the SKU table for a section."""
    keys_order = ["Size", "Material", "Head", "Drive", "Shank", "Fuel cell",
                  "Collation", "Pack size", "Pack", "Product Code", "Barcode"]
    price_keys = ["Price", "Price/pcs", "Price/pack"]
    special_keys = [k for k in section["items"][0].keys()
                    if any(k.startswith(x) for x in ("Special", "Pallet", "Over", "Carton"))
                    and k not in price_keys + keys_order]

    items = section["items"]
    used_keys = []
    for k in keys_order:
        if any(it.get(k) for it in items):
            used_keys.append(k)
    return used_keys, price_keys, special_keys


def render_sku_table(section, category_id, photo_map):
    items = section["items"]
    if not items:
        return ""
    used, price_keys, special_keys = headers_for_section(section, photo_map)
    # which price column actually has data
    price_col = next((p for p in price_keys if any(it.get(p) for it in items)), "Price")
    special_col = next((s for s in special_keys if any(it.get(s) for it in items)), "")

    th = "".join(f"<th>{esc(k)}</th>" for k in used)
    if price_col:
        th += f"<th>{esc(price_col)}</th>"
    if special_col:
        th += f"<th>{esc(special_col)}</th>"
    th += "<th></th>"

    rows = ""
    for it in items:
        slug = re.sub(r"[^a-z0-9]+", "-", it["sku"].lower()).strip("-")
        tds = ""
        for k in used:
            cls = ""
            if k == "Product Code":
                cls = ' class="code"'
            elif k == "Barcode":
                cls = ' class="barcode"'
            tds += f"<td{cls}>{esc(it.get(k, ''))}</td>"
        if price_col:
            v = it.get(price_col, "")
            tds += f'<td class="price">{("$" + esc(v)) if v else ""}</td>'
        if special_col:
            tds += f"<td>{esc(it.get(special_col, ''))}</td>"
        tds += f'<td><a href="../products/{slug}.html">View →</a></td>'
        rows += f"<tr>{tds}</tr>"

    return f'<table class="sku-table"><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table>'


def render_category(category, photo_map):
    blocks = ""
    for sec in category["sections"]:
        if not sec["items"]:
            continue
        blocks += f"""
        <div class="section-block">
          <div class="meta-row"><span class="pill">{len(sec['items'])} SKUs</span></div>
          <h3>{esc(sec['title'])}</h3>
          {render_sku_table(sec, category['id'], photo_map)}
        </div>"""

    body = f"""
  <section>
    <div class="container">
      <div class="crumbs"><a href="../index.html">Home</a> / <a href="../products.html">Products</a> / {esc(category['name'])}</div>
      <div class="section-head" style="text-align:left;">
        <span class="eyebrow">{category['total_skus']} SKUs · {len(category['sections'])} ranges</span>
        <h2>{esc(category['name'])}</h2>
        <p>{esc(category['blurb'])}</p>
      </div>
      <div class="search-box"><input placeholder="Search this category by SKU, size, material…" oninput="filterTable(this.value)"></div>
      {blocks}
    </div>
  </section>

  <script>
  function filterTable(query) {{
    const q = query.toLowerCase();
    document.querySelectorAll('.section-block').forEach(block => {{
      let any = false;
      block.querySelectorAll('tbody tr').forEach(tr => {{
        const text = tr.textContent.toLowerCase();
        const m = text.includes(q);
        tr.style.display = m ? '' : 'none';
        if (m) any = true;
      }});
      block.style.display = (any || !q) ? '' : 'none';
    }});
  }}
  </script>
"""
    return base_html(category["name"], body, "products", path_depth=1)


def render_product(item, category, section, photo_map):
    slug = re.sub(r"[^a-z0-9]+", "-", item["sku"].lower()).strip("-")
    sku = item["sku"]
    photo_files = photo_map.get(sku, [])
    if photo_files:
        photo_html = "".join(
            f'<img src="../assets/images/products/photos/{p}.jpg" alt="{esc(sku)} photo" loading="lazy">'
            for p in photo_files[:1]
        )
        img_block = f'<div class="img-wrap" style="padding:0; background:#fff;">{photo_html}</div>'
    else:
        img_block = f'<div class="img-wrap"><svg viewBox="0 0 400 200" width="100%"><use href="../assets/images/site/icons.svg#{CATEGORY_ICON[category["id"]]}"></use></svg></div>'

    spec_html = ""
    spec_keys = ["Size", "Material", "Head", "Drive", "Shank", "Fuel cell", "Collation", "Pack size", "Pack"]
    for k in spec_keys:
        v = item.get(k)
        if v:
            spec_html += f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>"
    spec_html += f"<dt>Product Code</dt><dd style='font-family:monospace;'>{esc(sku)}</dd>"
    if item.get("Barcode"):
        spec_html += f"<dt>Barcode</dt><dd style='font-family:monospace;'>{esc(item['Barcode'])}</dd>"

    price = item.get("Price") or item.get("Price/pack") or item.get("Price/pcs") or ""
    special = ""
    for k in ["Pallet Special", "Over 10 boxes", "Over 20packs", "Over 5packs",
              "Carton Special\nOver whole carton", "Special\nOver 10 Packs", "Over 5 packs", "No Special", "Pallet"]:
        if item.get(k) and item[k] not in ("/", ""):
            special = item[k]
            break

    price_html = ""
    if price:
        unit = "/pack" if "pack" in (
            item.get("Price/pack", "") or "") or "Price/pack" in item else "/pcs"
        if "Price/pcs" in item:
            unit = "/pcs"
        elif item.get("Price"):
            unit = ""
        price_html = f'<span class="pp">${esc(price)} <small>{unit}</small></span>'
        if special:
            price_html += f'<span class="vol">Volume: {esc(special)}</span>'

    body = f"""
  <section>
    <div class="container">
      <div class="crumbs"><a href="../index.html">Home</a> / <a href="../products.html">Products</a> / <a href="../category/{category['id']}.html">{esc(category['name'])}</a> / {esc(sku)}</div>
      <div class="product-hero">
        {img_block}
        <div>
          <span class="eyebrow" style="display:inline-block; padding:6px 14px; background:#fbe9d8; color:#c4631a; border-radius:999px; font-size:12px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase;">{esc(section['title'])}</span>
          <h1>{esc(item.get('Size', '') or 'Product')} <small style="color:#6b6b6b; font-weight:400; font-size:18px;">— {esc(item.get('Material', ''))}</small></h1>
          <p class="sub">SKU <b>{esc(sku)}</b> · Barcode {esc(item.get('Barcode', '—'))}</p>
          <dl class="spec-grid">{spec_html}</dl>
          {f'<div class="price-block">{price_html}</div>' if price_html else ''}
          <div class="product-cta">
            <a class="btn" href="../trade.html">Add to trade order</a>
            <a class="btn outline" href="../downloads.html" style="border-color:#1f1f1f; color:#1f1f1f;">Download spec PDF</a>
          </div>
          <p class="note" style="margin-top:24px;">Trade pricing shown above is list — your trade tier discount (typically 10%–20%) is applied at invoice. Pallet pricing available on request.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="related">
    <div class="container">
      <h2>Related products in this range</h2>
      <div class="cat-grid">
        {render_related(section, item, category)}
      </div>
    </div>
  </section>
"""
    return base_html(f"{sku} — {item.get('Size', '')}", body, "products", path_depth=1)


def render_related(section, current_item, category):
    related = [it for it in section["items"] if it["sku"] != current_item["sku"]][:3]
    html_blocks = ""
    for it in related:
        slug = re.sub(r"[^a-z0-9]+", "-", it["sku"].lower()).strip("-")
        html_blocks += f"""
          <a class="cat-card" href="{slug}.html">
            <div class="visual"><svg viewBox="0 0 400 200" width="280"><use href="../assets/images/site/icons.svg#{CATEGORY_ICON[category['id']]}"></use></svg></div>
            <div class="body">
              <h3>{esc(it.get('Size', '') or it['sku'])}</h3>
              <p>{esc(it.get('Material', ''))} · {esc(it.get('Pack size', '') or it.get('Pack', ''))}</p>
              <div class="meta"><span>{esc(it['sku'])}</span><a href="{slug}.html">View</a></div>
            </div>
          </a>"""
    return html_blocks


def render_catalog_print(category):
    """One printable HTML catalogue per category — designed to print to PDF."""
    rows = ""
    for sec in category["sections"]:
        rows += f"<h3 style='background:#1f1f1f; color:#fff; padding:8px 14px; margin:24px 0 0;'>{esc(sec['title'])}</h3>"
        rows += '<table style="width:100%; border-collapse:collapse; font-size:13px; margin-bottom:14px;"><thead style="background:#f5f5f5;"><tr>'
        keys = ["Size", "Material", "Pack size", "Pack", "Product Code", "Barcode"]
        used = [k for k in keys if any(it.get(k) for it in sec["items"])]
        for k in used:
            rows += f"<th style='text-align:left; padding:6px 10px; border:1px solid #ddd; text-transform:uppercase; font-size:11px; letter-spacing:0.6px;'>{esc(k)}</th>"
        # price
        any_price = any(it.get("Price") or it.get("Price/pack") or it.get("Price/pcs") for it in sec["items"])
        if any_price:
            rows += "<th style='text-align:left; padding:6px 10px; border:1px solid #ddd; text-transform:uppercase; font-size:11px;'>Price</th>"
        rows += "</tr></thead><tbody>"
        for it in sec["items"]:
            rows += "<tr>"
            for k in used:
                rows += f"<td style='padding:6px 10px; border:1px solid #ddd;'>{esc(it.get(k,''))}</td>"
            if any_price:
                p = it.get("Price") or it.get("Price/pack") or it.get("Price/pcs") or ""
                rows += f"<td style='padding:6px 10px; border:1px solid #ddd; font-weight:600; color:#c4631a;'>{'$' + esc(p) if p else ''}</td>"
            rows += "</tr>"
        rows += "</tbody></table>"

    body = f"""
<style>
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #1f1f1f; max-width: 900px; margin: 0 auto; padding: 40px 24px; }}
  h1 {{ color: #c4631a; }}
  @media print {{ .no-print {{ display: none; }} }}
</style>
<div class="no-print" style="background:#1f1f1f; color:#fff; padding:14px 24px; margin-bottom:24px; border-radius:6px;">
  <b>Catalogue: {esc(category['name'])}</b> — Print this page or save as PDF (⌘P).
</div>
<header style="border-bottom:3px solid #E87722; padding-bottom:16px; margin-bottom:24px;">
  <h1 style="margin:0; font-size:28px;">{esc(category['name'])}</h1>
  <p style="color:#6b6b6b; margin:4px 0;">Kiwi Nails Fasteners Ltd · {category['total_skus']} SKUs · Issue 2026-05</p>
</header>
<p style="font-size:14px; color:#6b6b6b;">{esc(category['blurb'])}</p>
{rows}
<footer style="margin-top:48px; padding-top:16px; border-top:1px solid #ddd; font-size:11px; color:#888;">
  Kiwi Nails Fasteners Ltd · Auckland, New Zealand · sales@kiwinails.co.nz · +64 9 887 1230 · Director: Linda Kong<br>
  All prices in NZD ex GST. Trade pricing discounts of 10%–20% applied at invoice. BPIR documentation available on request.
</footer>
"""
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{esc(category['name'])} Catalogue</title></head><body>{body}</body></html>"


def render_bpir():
    body = """
<style>
  body { font-family: 'Helvetica Neue', Arial, sans-serif; color:#1f1f1f; max-width: 880px; margin:0 auto; padding:48px 32px; line-height:1.55; }
  h1 { color:#c4631a; border-bottom:3px solid #E87722; padding-bottom:12px; }
  h2 { margin-top:32px; color:#1f1f1f; }
  table { width:100%; border-collapse: collapse; font-size:14px; margin: 12px 0; }
  td, th { border:1px solid #ddd; padding:10px 12px; text-align:left; vertical-align:top; }
  th { background:#f5f5f5; }
  .label { color:#6b6b6b; font-size:13px; }
  .sig-block { margin-top:48px; border-top:2px solid #1f1f1f; padding-top:24px; }
  .sig { display: grid; grid-template-columns: 1fr 1fr; gap:32px; margin-top:32px; }
  .sig-line { border-bottom:1px solid #1f1f1f; height:48px; }
  @media print { .no-print { display:none; } body { padding:24px; } }
</style>

<div class="no-print" style="background:#1f1f1f; color:#fff; padding:14px 24px; margin: -48px -32px 32px; border-radius:0;">
  <b>BPIR Declaration</b> — Print this page or save as PDF (⌘P). Linda Kong to sign and date before issue to customers.
</div>

<h1>Building Product Information Requirements (BPIR) Declaration</h1>
<p class="label">Issued under Section 362T of the Building Act 2004 and the Building (Building Product Information Requirements) Regulations 2022.</p>

<h2>1. Manufacturer / Importer</h2>
<table>
  <tr><th style="width:34%;">Legal entity</th><td>Kiwi Nails Fasteners Ltd</td></tr>
  <tr><th>NZBN</th><td>[to be inserted before issue]</td></tr>
  <tr><th>Trading address</th><td>Auckland, New Zealand</td></tr>
  <tr><th>Contact</th><td>sales@kiwinails.co.nz · +64 9 887 1230</td></tr>
  <tr><th>Authorised representative</th><td>Linda Kong, Director</td></tr>
</table>

<h2>2. Product range covered</h2>
<p>This declaration covers all 412 SKUs supplied by Kiwi Nails Fasteners Ltd across the following product families:</p>
<ul>
  <li><b>Hardware</b> — Sheet brace strap, CPC, joist hangers, stud strap, square washer, threaded rod, soakers, W-Flash, pin anchors, drive pin, wire dog</li>
  <li><b>Screws</b> — Decking, bugle batten, HWF (Tek), chipboard, purlin, jolt-head screws</li>
  <li><b>Collated Gun Nails</b> — 34° paper-collated D-head, jolt-head weatherboard, round-head, joist-hanger nails, staples, brads</li>
  <li><b>Coil Nails</b> — Round-head, jolt-head weatherboard, shingle roofing, industrial, roofing tile</li>
  <li><b>Bolts</b> — Engineering, coach, coach screw, screw bolt, through bolt</li>
  <li><b>Loose Nails</b> — Flat-head, jolt-head, rose-head, clinch, decking, fibre cement, fencing, clout, underlay, product, soaker, panel pin, roofing, fencing batten staple</li>
</ul>
<p class="label">Each SKU's specific size, material grade and pack size is listed in the corresponding product page on kiwinails.co.nz or the printed catalogue.</p>

<h2>3. Intended use</h2>
<p>Products are intended for use in light timber-framed construction (NZS 3604), structural steel works (AS/NZS 1554), exposed and concealed timber jointing, roofing and cladding (NZS 3604, E2/AS1), fencing, and general carpentry. Material grade and fastener selection must follow the project's structural engineer's design and the relevant New Zealand Building Code clauses.</p>

<h2>4. Materials and finishes</h2>
<table>
  <tr><th>Bright steel</th><td>Low-carbon steel, untreated. Internal / dry environments only.</td></tr>
  <tr><th>HD Galvanised (HD Galv)</th><td>Hot-dip zinc coated to AS/NZS 4680. Suitable for external and treated-timber contact.</td></tr>
  <tr><th>Stainless Steel 304 (S/ST304)</th><td>Austenitic stainless to AISI 304. Suitable for general external use, treated timber contact.</td></tr>
  <tr><th>Stainless Steel 316 (S/ST316)</th><td>Marine-grade austenitic stainless to AISI 316. Suitable for coastal &amp; marine environments.</td></tr>
  <tr><th>Silicon Bronze</th><td>CuSi3Mn1 alloy. Boat-building and high-corrosion applications.</td></tr>
  <tr><th>Ruspert coating</th><td>Multi-layer corrosion-resistant coating for batten / hex screws. Suitable for exterior structural use.</td></tr>
</table>

<h2>5. New Zealand Building Code compliance</h2>
<table>
  <tr><th>B1 Structure</th><td>Products meet the fastener schedule requirements of NZS 3604 §2.4 and tables 4.10–4.13 when correctly specified and installed.</td></tr>
  <tr><th>B2 Durability</th><td>Material grade selection (HD Galv, S/ST304, S/ST316, Silicon Bronze) provides minimum 50-year durability when matched to exposure zone per E2/AS1 Table 20.</td></tr>
  <tr><th>E2 External moisture</th><td>Stainless and silicon-bronze fasteners suitable for sea-spray zone D per E2/AS1.</td></tr>
  <tr><th>F2 Hazardous building materials</th><td>Products contain no lead, no cadmium, no asbestos. RoHS compliant.</td></tr>
</table>

<h2>6. Marking, packaging and traceability</h2>
<p>Every retail pack carries a GS1-NZ registered EAN-13 barcode in the prefix range 9420052xxxxxx. The pack label states product code, size, material, pack size, and country of manufacture (China, under Kiwi Nails Fasteners Ltd QA). Batch traceability is maintained for 7 years against import / shipment records.</p>

<h2>7. Limitations &amp; safe-use information</h2>
<ul>
  <li>This declaration is not a substitute for specific engineering design. Specifier must verify suitability of fastener type, size and spacing for each application.</li>
  <li>Bright steel must not be used in external or pressure-treated timber applications.</li>
  <li>HD Galv must not be used in continuous direct contact with stainless steel or aluminium where moisture is present (galvanic corrosion risk).</li>
  <li>Pneumatic gun nails must be driven with a tool compatible with the collation type (34° paper, plastic coil, wire coil) and within the manufacturer's recommended pressure range (typically 5.5–8.3 bar / 80–120 psi).</li>
</ul>

<h2>8. Declaration</h2>
<p>I, the undersigned, declare on behalf of Kiwi Nails Fasteners Ltd that the information contained in this Building Product Information Requirements declaration is accurate to the best of my knowledge as at the date of signing, and that the products described are supplied with the warranties and limitations set out above.</p>

<div class="sig-block">
  <div class="sig">
    <div>
      <div class="label">Signed</div>
      <div class="sig-line"></div>
      <div style="margin-top:6px;"><b>Linda Kong</b><br><span class="label">Director, Kiwi Nails Fasteners Ltd</span></div>
    </div>
    <div>
      <div class="label">Date</div>
      <div class="sig-line"></div>
      <div style="margin-top:6px;" class="label">Place: Auckland, New Zealand</div>
    </div>
  </div>
</div>

<p style="margin-top:48px; font-size:11px; color:#888;">
This declaration is reviewed annually and on any product specification change. Document reference KNF-BPIR-2026-05 · v1.0
</p>
"""
    return f"<!doctype html><html><head><meta charset='utf-8'><title>BPIR Declaration — Kiwi Nails</title></head><body>{body}</body></html>"


def render_material_compliance():
    body = """
<style>
  body { font-family: 'Helvetica Neue', Arial, sans-serif; color:#1f1f1f; max-width:880px; margin:0 auto; padding:48px 32px; line-height:1.55; }
  h1 { color:#c4631a; border-bottom:3px solid #E87722; padding-bottom:12px; }
  table { width:100%; border-collapse: collapse; margin:14px 0; font-size:14px; }
  th, td { border:1px solid #ddd; padding:10px 12px; text-align:left; }
  th { background:#f5f5f5; }
  @media print { .no-print { display:none; } }
</style>
<div class="no-print" style="background:#1f1f1f; color:#fff; padding:14px 24px; margin:-48px -32px 32px;">
  <b>Material Compliance Statement</b> — Print or save as PDF.
</div>
<h1>Material Compliance Statement</h1>
<p>This statement supports the BPIR declaration for all products supplied by Kiwi Nails Fasteners Ltd. It cross-references the material grades used in our product range against the relevant Australian / New Zealand Standards.</p>

<h2>Material grade reference</h2>
<table>
  <tr><th>Trade name</th><th>Specification</th><th>Standard</th><th>Typical durability zone (E2/AS1)</th></tr>
  <tr><td>Bright steel</td><td>Low carbon steel, mill-bright finish</td><td>AS 1397 (base), uncoated</td><td>Internal / dry only</td></tr>
  <tr><td>HD Galvanised</td><td>Hot-dip galvanised, ≥45 μm zinc</td><td>AS/NZS 4680</td><td>Zone B / C (sheltered exterior)</td></tr>
  <tr><td>S/ST304</td><td>X5CrNi18-10 austenitic stainless</td><td>AS 1449 / AISI 304</td><td>Zone C / D (general exterior)</td></tr>
  <tr><td>S/ST316</td><td>X5CrNiMo17-12-2 austenitic stainless</td><td>AS 1449 / AISI 316</td><td>Zone D (sea spray)</td></tr>
  <tr><td>Silicon bronze</td><td>CuSi3Mn1 wrought alloy</td><td>BS 2874 CZ128</td><td>Zone D (marine)</td></tr>
  <tr><td>Ruspert</td><td>Multi-layer Zn + ceramic + organic top coat</td><td>JIS H 8610 equivalent</td><td>Zone B / C (exterior structural)</td></tr>
</table>

<h2>Quality assurance</h2>
<p>Materials are sourced from ISO 9001-certified mills and fastener manufacturers in mainland China. Each consignment is inspected on arrival in Auckland for dimensional tolerance (±0.05mm on shank diameter) and coating thickness (per AS/NZS 4680 for HD Galv). Records are retained for seven years.</p>

<p style="margin-top:48px;"><b>Linda Kong</b><br>Director, Kiwi Nails Fasteners Ltd<br>Auckland, New Zealand</p>
"""
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Material Compliance — Kiwi Nails</title></head><body>{body}</body></html>"


def render_barcode_statement():
    body = """
<style>
  body { font-family: 'Helvetica Neue', Arial, sans-serif; color:#1f1f1f; max-width:880px; margin:0 auto; padding:48px 32px; line-height:1.55; }
  h1 { color:#c4631a; border-bottom:3px solid #E87722; padding-bottom:12px; }
  @media print { .no-print { display:none; } }
</style>
<div class="no-print" style="background:#1f1f1f; color:#fff; padding:14px 24px; margin:-48px -32px 32px;">
  <b>Barcode Range Statement</b> — Print or save as PDF.
</div>
<h1>GS1-NZ Barcode Range Statement</h1>
<p>Kiwi Nails Fasteners Ltd is a registered member of GS1 New Zealand. All retail and trade pack barcodes are issued from our allocated GTIN range under the company prefix <b>9420052</b>.</p>
<p>This guarantees that every Kiwi Nails SKU has a unique, NZ-registered EAN-13 barcode that is scan-compatible with all major point-of-sale systems used by New Zealand merchants — including Vend, Lightspeed, Pronto, Triquestra, Citrix RetailIQ and Counterpoint.</p>

<h2>Format</h2>
<p>Each barcode is a 13-digit EAN-13: <code>9 420052 XXXXXX C</code> where XXXXXX is the unique product index and C is the check digit. The check digit follows the standard EAN-13 algorithm.</p>

<h2>Use restrictions</h2>
<p>Retailers must scan and price each unit individually. Re-packing under a different barcode (PLU) is permitted but the original Kiwi Nails barcode must remain visible on the outer carton for traceability.</p>

<p style="margin-top:48px;"><b>Linda Kong</b><br>Director, Kiwi Nails Fasteners Ltd</p>
"""
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Barcode Statement — Kiwi Nails</title></head><body>{body}</body></html>"


def main():
    catalog = json.loads(DATA.read_text())
    photo_map_path = ROOT / "js" / "photo_map.json"
    photo_map = json.loads(photo_map_path.read_text()) if photo_map_path.exists() else {}

    # Top-level pages
    (ROOT / "index.html").write_text(render_home(catalog))
    (ROOT / "about.html").write_text(render_about(catalog))
    (ROOT / "products.html").write_text(render_products(catalog))
    (ROOT / "trade.html").write_text(render_trade(catalog))
    (ROOT / "contact.html").write_text(render_contact())
    (ROOT / "downloads.html").write_text(render_downloads(catalog))
    print("✓ top-level pages")

    # Category pages
    (ROOT / "category").mkdir(exist_ok=True)
    for c in catalog["categories"]:
        (ROOT / "category" / f"{c['id']}.html").write_text(render_category(c, photo_map))
    print(f"✓ {len(catalog['categories'])} category pages")

    # Product pages
    (ROOT / "products").mkdir(exist_ok=True)
    count = 0
    for c in catalog["categories"]:
        for sec in c["sections"]:
            for it in sec["items"]:
                slug = re.sub(r"[^a-z0-9]+", "-", it["sku"].lower()).strip("-")
                (ROOT / "products" / f"{slug}.html").write_text(render_product(it, c, sec, photo_map))
                count += 1
    print(f"✓ {count} product pages")

    # Printable catalogue per category
    (ROOT / "catalogs").mkdir(exist_ok=True)
    for c in catalog["categories"]:
        (ROOT / "catalogs" / f"{c['id']}.html").write_text(render_catalog_print(c))
    print(f"✓ {len(catalog['categories'])} printable catalogs")

    # Compliance docs
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "bpir-declaration.html").write_text(render_bpir())
    (ROOT / "docs" / "material-compliance.html").write_text(render_material_compliance())
    (ROOT / "docs" / "barcode-statement.html").write_text(render_barcode_statement())
    print("✓ compliance docs")

    print("\nSite generation complete.")


if __name__ == "__main__":
    main()
