#!/usr/bin/env python3
"""Render Midtown handout + TV screens from menu.json and export PDF/PNG."""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
MENU_PATH = ROOT / "menu.json"
ASSET = ROOT / "assets"
GEN = ASSET / "generated"
LOGO_SRC = ROOT.parent / "brand-kit" / "logos" / "primary_logo_lockup.png"
FONT_OSWALD = ROOT / "fonts" / "Oswald[wght].ttf"
CHROME = shutil.which("google-chrome") or shutil.which("google-chrome-stable")

FORBIDDEN = (
    "$0.00",
    "to confirm",
    "closing time",
    "BEVERAGES.",
    "DESSERTS.",
    "Strawberry Banana",
    "Strawberry Lemon",
    "Jalapeño Cheese Corn Bread",
    "Jalapeno Cheese Corn Bread",
    "Meat Sampler",
)


def load_menu():
    return json.loads(MENU_PATH.read_text())


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def price_cells(prices):
    kind = f"n{len(prices)}"
    cells = "".join(f"<span>{esc(p)}</span>" for p in prices)
    return f'<span class="prices {kind}">{cells}</span>'


def item_row(item, headers=None, choiceNotePrefix=""):
    name = esc(item["name"])
    if item.get("portion"):
        name += f' <span class="portion">{esc(item["portion"])}</span>'
    if "prices" in item:
        price = price_cells(item["prices"])
    else:
        price = f'<span class="price">{esc(item["price"])}</span>'
    row = (
        f'<div class="item"><span class="name">{name}</span>'
        f'<span class="leaders"></span>{price}</div>'
    )
    extra = ""
    if item.get("detail"):
        extra += f'<p class="detail">{esc(item["detail"])}</p>'
    if item.get("after"):
        extra += f'<p class="choice-note">{esc(choiceNotePrefix)}{esc(item["after"])}</p>'
    if item.get("choiceNote"):
        extra += f'<p class="choice-note">{esc(choiceNotePrefix)}{esc(item["choiceNote"])}</p>'
    return row + extra


def header_row(headers):
    return (
        '<div class="item heads"><span class="name">&nbsp;</span><span class="leaders"></span>'
        + price_cells(headers)
        + "</div>"
    )


def render_section(section, sid=None) -> str:
    if section.get("groups"):
        # For sections with groups, only render the groups (each group has its own section)
        return "".join(render_group(g, section["title"], section) for g in section.get("groups", []))
    
    if section.get("price"):
        head = (
            '<div class="section-head"><h2>'
            + esc(section["title"])
            + '</h2><span class="leaders"></span><span class="price">'
            + esc(section["price"])
            + "</span></div>"
        )
    elif section.get("priceHeaders"):
        # For sections with priceHeaders (like Sides, Whole Wings)
        # Include the headers inline with the title, with leaders for alignment
        head = (
            '<div class="section-head"><h2>'
            + esc(section["title"])
            + '</h2><span class="leaders"></span>'
            + price_cells(section["priceHeaders"])
            + "</div>"
        )
    else:
        head = f'<h2>{esc(section["title"])}</h2>'
    sid_attr = f' id="section-{sid}"' if sid else ''
    parts = [f'<section class="section"{sid_attr}>{head}']
    if section.get("subheader"):
        parts.append(f'<h3 class="subheader">{esc(section["subheader"])}</h3>')
    if section.get("heroImage"):
        # Handle both full paths and relative paths
        hero_path = section["heroImage"]
        if not hero_path.startswith("assets/"):
            hero_path = f"assets/generated/{esc(section['heroImage'])}"
        parts.append(f'<img class="section-hero-image" src="{esc(hero_path)}" alt="{esc(section["title"])}">')
    if section.get("image"):
        parts.append(f'<img class="section-image" src="assets/generated/{esc(section["image"])}" alt="{esc(section["title"])}">')
    if section.get("note"):
        # Crazy Potato note reads better under the price line.
        if section["title"] != "Crazy Potato":
            parts.append(f'<p class="note">{esc(section["note"])}</p>')
    for item in section.get("items", []):
        parts.append(item_row(item, choiceNotePrefix=section.get("choiceNotePrefix", "")))
    for item in section.get("single", []):
        parts.append(item_row(item, choiceNotePrefix=section.get("choiceNotePrefix", "")))
    if section.get("offers"):
        for item in section["offers"]:
            parts.append(item_row(item, choiceNotePrefix=section.get("choiceNotePrefix", "")))
    if section.get("choices"):
        label = section.get("choicesLabel")
        prefix = section.get("choicesLabelPrefix", "")
        if label:
            parts.append(f'<p class="choices-label">{esc(prefix)}{esc(label)}</p>')
        lis = "".join(f"<li>{esc(c)}</li>" for c in section["choices"])
        parts.append(f'<ul class="choices">{lis}</ul>')
    if section.get("choiceNote"):
        prefix = section.get("choiceNotePrefix", "")
        parts.append(f'<p class="choice-note">{esc(prefix)}{esc(section["choiceNote"])}</p>')
    if section["title"] == "Crazy Potato" and section.get("note"):
        parts.append(f'<p class="note">{esc(section["note"])}</p>')
    parts.append("</section>")
    return "".join(parts)


def render_group(group, section_title, section=None) -> str:
    """Render a single group from a section with groups."""
    if group.get("priceHeaders"):
        head = (
            '<div class="section-head"><h2>'
            + esc(section_title)
            + '</h2><span class="leaders"></span>'
            + price_cells(group["priceHeaders"])
            + "</div>"
        )
    else:
        head = f'<h2>{esc(section_title)}</h2>'
    parts = [f'<section class="section">{head}']
    if section and section.get("heroImage"):
        # Handle both full paths and relative paths
        hero_path = section["heroImage"]
        if not hero_path.startswith("assets/"):
            hero_path = f"assets/generated/{esc(section['heroImage'])}"
        parts.append(f'<img class="section-hero-image" src="{esc(hero_path)}" alt="{esc(section_title)}">')
    for item in group.get("items", []):
        parts.append(item_row(item, choiceNotePrefix=group.get("choiceNotePrefix", "")))
    if group.get("choiceNote"):
        prefix = group.get("choiceNotePrefix", "")
        parts.append(f'<p class="choice-note">{esc(prefix)}{esc(group["choiceNote"])}</p>')
    parts.append("</section>")
    return "".join(parts)


def render_columns(menu, column_ids) -> str:
    cols = []
    for ids in column_ids:
        body = "".join(render_section(menu["sections"][sid]) for sid in ids)
        cols.append(f'<div class="col">{body}</div>')
    return f'<div class="columns">{"".join(cols)}</div>'


def render_mast(menu) -> str:
    c = menu["contact"]
    order_domain = (
        '<div class="order-domain">'
        '<a href="https://midtownbbq.io" target="_blank" class="order-domain-link">'
        '<span class="order-domain-prefix">order online:</span>'
        '<span class="order-domain-text">midtownbbq.io</span>'
        "</a>"
        "</div>"
    )
    return f'''<header class="mast">
      <img class="logo" src="assets/logo-lockup.png" alt="Midtown Smokehouse. {esc(menu["tagline"])}">
      <div class="contact">
        {order_domain}
        <div>{esc(c["street"])}</div>
        <div>{esc(c["city"])}</div>
        <div class="phone">{esc(c["phone"])}</div>
      </div>
    </header>'''


HOUR_DAY_TOKENS = ("MON", "TUE–FRI", "SAT", "SUN")


def render_hours(menu) -> str:
    """Day labels in white, the rest of the line in yellow."""
    text = esc(menu["hoursFooter"])
    for token in HOUR_DAY_TOKENS:
        text = text.replace(token, f'<span class="white">{token}</span>')
    return f'<footer class="hours">{text}</footer>'


def render_contact_footer(menu) -> str:
    c = menu["contact"]
    qr_code = '<a href="https://order.mts.moldvan.com" target="_blank" class="qr-code-container">'
    qr_code += '<img class="qr-code-image" src="assets/generated/qr-order.png" alt="Order online QR code">'
    qr_code += '<span class="qr-code-label">Order online</span>'
    qr_code += "</a>"
    return (
        '<footer class="hours contact-line">'
        f'{esc(c["street"])} · {esc(c["city"])} · '
        f'<span class="phone">{esc(c["phone"])}</span> · '
        f'{qr_code}</footer>'
    )


def render_screen_footer(menu, screen) -> str:
    if screen.get("footer") == "contact":
        return render_contact_footer(menu)
    return render_hours(menu)


def page_shell(title, body, extra_class="", page_css="") -> str:
    extra = f"<style>{page_css}</style>" if page_css else ""
    controls = '''  <div class="background-controls">
    <select class="bg-select" id="bgSelect">
      <option value="" disabled selected>Choose background...</option>
      <option value="charcoal">Charcoal</option>
      <option value="wood">Wood</option>
      <option value="dark">Dark</option>
      <option value="charcoal-texture">Charcoal Texture (bright)</option>
      <option value="brisket-hero">Brisket Hero</option>
      <option value="pulled-hero">Pulled Hero</option>
      <option value="ribs-hero">Ribs Hero</option>
      <option value="burntends-hero">Burnt Ends</option>
      <option value="flux-a">Flux A</option>
      <option value="flux-b">Flux B</option>
      <option value="v3-9090">V3 9090</option>
      <option value="v3-4242">V3 4242</option>
      <option value="ribstack">Ribstack</option>
      <option value="cubes-a">Cubes A</option>
      <option value="cubes-b">Cubes B</option>
    </select>
  </div>'''
    script = '''  <script>
    const select = document.getElementById('bgSelect');
    const body = document.body;
    
    // Set default to charcoal-texture on load
    if (select.value === '') {
      body.className += ' background-charcoal-texture';
      select.value = 'charcoal-texture';
    }
    
    select.addEventListener('change', () => {
      const val = select.value;
      if (val) {
        body.className = body.className.replace(/background-\\w+/g, '');
        body.className += ` background-${val}`;
      }
    });
  </script>'''
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{esc(title)}</title>
  <link rel="stylesheet" href="styles/menu.css">
  {extra}
</head>
<body class="{extra_class}">
{controls}
{body}
{script}
</body>
</html>
'''


def write_handout(menu) -> None:
    pages = []
    page_labels = {"page-1": "Front", "page-2": "Back"}
    for page in menu["handoutPages"]:
        # Default rendering
        inner = render_mast(menu) + render_columns(menu, page["columns"]) + render_hours(menu)

        # Override for front page
        if page["id"] == "page-1":
            mast = render_mast(menu)
            # Any section with an `image` renders as a full-width photo panel
            # (.side-section) inside its column; everything else is a normal
            # text section. Columns stack in menu order.
            cols_html = []
            for col_ids in page["columns"]:
                col_parts = []
                for sid in col_ids:
                    sec = menu["sections"][sid]
                    sec_html = render_section(sec, sid)
                    # Any section with an `image` or `heroImage` and a section-head
                    # (i.e. a priced section) renders as a full-width photo panel
                    # (.side-section); the image becomes the dimmed background
                    # behind the title + text. Plain <h2> sections like Sandwiches
                    # stay as normal text sections.
                    img_raw = sec.get("image") or sec.get("heroImage")
                    if img_raw:
                        # Only turn sections with minimal content into photo panels.
                        # Sections with long item lists (e.g. Sandwiches) stay as
                        # normal text sections with their inline hero image.
                        item_count = len(sec.get("items", [])) + len(sec.get("offers", []))
                        if item_count <= 2:
                            img_src = img_raw if img_raw.startswith("assets/") else f'assets/generated/{img_raw}'
                            # Drop the inline  tag; it becomes the dimmed background
                            # layer behind the title + text (text stays full brightness).
                            sec_html = sec_html.replace(
                                f'<img class="section-image" src="{img_src}" alt="{sec["title"]}">',
                                '',
                            ).replace(
                                f'<img class="section-hero-image" src="{img_src}" alt="{sec["title"]}">',
                                '',
                            )
                            m = re.match(
                                r'^(<section class="section"[^>]*><div class="section-head">.*?</div>)(.*)</section>$',
                                sec_html,
                                re.S,
                            )
                            if m:
                                head, tail = m.group(1), m.group(2)
                            else:
                                # Sections without section-head (e.g. Combos: just <h2>)
                                m = re.match(
                                    r'^(<section class="section"[^>]*><h2>.*?</h2>)(.*)</section>$',
                                    sec_html,
                                    re.S,
                                )
                                if m:
                                    head, tail = m.group(1), m.group(2)
                                    hm = re.match(r'(<h2>.*?</h2>)(.*)', head, re.S)
                                    if hm:
                                        head = f'<div class="section-head">{hm.group(1)}{hm.group(2)}</div>'
                                else:
                                    head = tail = None
                            if head:
                                head_panel = head.replace('class="section"', 'class="section side-section"', 1)
                                sec_html = (
                                    f'{head_panel}'
                                    f'<div class="side-photo">'
                                    f'<img class="section-bg-img" src="{img_src}" alt="{esc(sec["title"])}">'
                                    f'{tail}'
                                    f'</div></section>'
                                )
                    col_parts.append(sec_html)
                cols_html.append(f'<div class="col">{"".join(col_parts)}</div>')
            inner = mast + f'<div class="columns">{"".join(cols_html)}</div>' + render_hours(menu)

        # Override for back page — combos gets the hero image behind its text
        if page["id"] == "page-2":
            mast = render_mast(menu)
            cols_html = []
            for col_ids in page["columns"]:
                col_parts = []
                for sid in col_ids:
                    sec = menu["sections"][sid]
                    sec_html = render_section(sec, sid)
                    img_raw = sec.get("image") or sec.get("heroImage")
                    if img_raw:
                        # Only turn sections with minimal content into photo panels.
                        # Sections with long item lists (e.g. Sandwiches) stay as
                        # normal text sections with their inline hero image.
                        item_count = len(sec.get("items", [])) + len(sec.get("offers", []))
                        if item_count <= 2:
                            img_src = img_raw if img_raw.startswith("assets/") else f'assets/generated/{img_raw}'
                            sec_html = sec_html.replace(
                                f'<img class="section-image" src="{img_src}" alt="{sec["title"]}">',
                                '',
                            ).replace(
                                f'<img class="section-hero-image" src="{img_src}" alt="{sec["title"]}">',
                                '',
                            )
                            m = re.match(
                                r'^(<section class="section"[^>]*><div class="section-head">.*?</div>)(.*)</section>$',
                                sec_html,
                                re.S,
                            )
                            if m:
                                head, tail = m.group(1), m.group(2)
                            else:
                                m = re.match(
                                    r'^(<section class="section"[^>]*><h2>.*?</h2>)(.*)</section>$',
                                    sec_html,
                                    re.S,
                                )
                                if m:
                                    head, tail = m.group(1), m.group(2)
                                    hm = re.match(r'(<h2>.*?</h2>)(.*)', head, re.S)
                                    if hm:
                                        head = f'<div class="section-head">{hm.group(1)}{hm.group(2)}</div>'
                                else:
                                    head = tail = None
                            if head:
                                head_panel = head.replace('class="section"', 'class="section side-section"', 1)
                                sec_html = (
                                    f'{head_panel}'
                                    f'<div class="side-photo">'
                                    f'<img class="section-bg-img" src="{img_src}" alt="{esc(sec["title"])}">'
                                    f'{tail}'
                                    f'</div></section>'
                                )
                    col_parts.append(sec_html)
                cols_html.append(f'<div class="col">{"".join(col_parts)}</div>')
            inner = mast + f'<div class="columns">{"".join(cols_html)}</div>' + render_hours(menu)

        page_id = esc(page["id"])
        label = esc(page_labels.get(page["id"], page["id"]))
        pages.append(f'<div class="page-label">{label}</div>')
        pages.append(f'<article class="page" id="{page_id}">{inner}</article>')

    page_css = (
        "@page { size: letter portrait; margin: 0; }"
        "#page-1 .side-section{position:relative;color:white;display:flex;flex-direction:column;}"
        "#page-1 .side-section::before{content:\"\";position:absolute;inset:0;background:rgba(0,0,0,0.45);z-index:1;}"
        "#page-1 .side-section > *{position:relative;z-index:2;}"
        "#page-1 .side-section .side-photo{position:relative;z-index:2;flex:1;min-height:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;}"
        "#page-1 .side-section .section-bg-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:brightness(0.5);z-index:0;pointer-events:none;display:block;}\n#page-1 .side-section .section-head h2{font-size:22px;padding-top:0.08in;font-family:Oswald,Impact,sans-serif;font-weight:900;text-shadow:0 2px 10px rgba(0,0,0,0.95);color:white!important;}"
        "#page-1 .side-section .side-photo > p{position:relative;z-index:2;margin:0 0.12in;font-size:17px;line-height:1.45;max-width:92%;font-family:Oswald,Impact,sans-serif;font-weight:600;text-shadow:0 2px 10px rgba(0,0,0,0.95);color:white!important;}"
        "#page-1 .side-section .side-photo > p.choice-note{font-size:13px;font-weight:500;text-transform:none;margin-top:0.10in;}"
        "#page-1 .mast{background:transparent;padding:0.12in 0.18in;border-radius:6px;margin-bottom:0.06in;}"
        "#page-1 .col{justify-content:flex-start;}"
        "#page-1 #section-wings .section-hero-image{max-height:1.7in;}"
        "#page-2 .side-section{position:relative;color:white;display:flex;flex-direction:column;}"
        "#page-2 .side-section::before{content:\"\";position:absolute;inset:0;background:rgba(0,0,0,0.45);z-index:1;}"
        "#page-2 .side-section > *{position:relative;z-index:2;}"
        "#page-2 .side-section .side-photo{position:relative;z-index:2;flex:1;min-height:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;}"
        "#page-2 .side-section .section-bg-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:brightness(0.5);z-index:0;pointer-events:none;display:block;}\n#page-2 .side-section .section-head h2{font-size:22px;padding-top:0.08in;font-family:Oswald,Impact,sans-serif;font-weight:900;text-shadow:0 2px 10px rgba(0,0,0,0.95);color:white!important;}"
        "#page-2 .side-section .side-photo > p{position:relative;z-index:2;margin:0 0.12in;font-size:17px;line-height:1.45;max-width:92%;font-family:Oswald,Impact,sans-serif;font-weight:600;text-shadow:0 2px 10px rgba(0,0,0,0.95);color:white!important;}"
        "#page-2 .side-section .side-photo > p.choice-note{font-size:13px;font-weight:500;text-transform:none;margin-top:0.10in;}"
        ".page-label{color:var(--yellow);font-family:Oswald,Impact,sans-serif;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;font-size:20px;margin:0 0 0.12in 0;text-shadow:0 2px 8px rgba(0,0,0,0.9);}"
    )
    html_doc = page_shell(
        "Midtown Smokehouse menu handout",
        "\n".join(pages),
        page_css=page_css,
    )
    (ROOT / "handout.html").write_text(html_doc)


def write_screens(menu) -> None:
    blocks = []
    for screen in menu["screens"]:
        bg = screen.get("background", "background.jpg")
        inner = (
            f'<img class="logo logo-hero" src="assets/logo-lockup.png" alt="Midtown Smokehouse. {esc(menu["tagline"])}">'
            + render_columns(menu, screen["columns"])
            + render_screen_footer(menu, screen)
        )
        klass = "screen compact" if screen.get("compact") else "screen"
        block = (
            f'<article class="{klass}" id="{esc(screen["id"])}" '
            f'style="--screen-photo: url(\'../assets/{esc(bg)}\')">{inner}</article>'
        )
        blocks.append(block)
        doc = page_shell(
            f'Midtown Smokehouse TV {screen["title"]}',
            block,
            extra_class="screen-page background-charcoal",
            page_css=(
                "@page { size: 1280px 720px; margin: 0; }"
                "html, body { width: 1280px; height: 720px; margin: 0; overflow: hidden; }"
            ),
        )
        (ROOT / f'screen-{screen["id"]}.html').write_text(doc)
    gallery = page_shell(
        "Midtown Smokehouse TV menus",
        '<div class="preview-wrap"><h1>TV menus · 4 screens · 1280 × 720</h1>'
        + "".join(blocks)
        + "</div>",
    )
    (ROOT / "screens.html").write_text(gallery)


def tracked_text(draw, text, font, y, fill, tracking, width, shadow=None):
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = (width - total) / 2
    if shadow:
        sx, sy, sc = shadow
        xx = x
        for ch, w in zip(text, widths):
            draw.text((xx + sx, y + sy), ch, font=font, fill=sc)
            xx += w + tracking
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking


def composite_logo(menu) -> None:
    # logo_lockup_v2.png is the current lockup: the previous badge with
    # LOW & SLOW. DONE RIGHT. stamped along the shield's own chevron edge.
    v2_logo = ROOT / "assets" / "generated" / "logo_lockup_v2.png"
    if v2_logo.exists():
        logo = Image.open(v2_logo).convert("RGBA")
        logo = logo.crop(logo.getbbox())
        ASSET.mkdir(parents=True, exist_ok=True)
        logo.save(ASSET / "logo-lockup.png")
        return
    flux_logo = ROOT / "assets" / "generated" / "logo_flux.png"
    if flux_logo.exists():
        logo = Image.open(flux_logo).convert("RGBA")
        logo = logo.crop(logo.getbbox())
        ASSET.mkdir(parents=True, exist_ok=True)
        logo.save(ASSET / "logo-lockup.png")
        return
    logo = Image.open(LOGO_SRC).convert("RGBA")
    bbox = logo.getbbox()
    logo = logo.crop(bbox)
    target_w = 1200
    logo = logo.resize(
        (target_w, round(logo.height * target_w / logo.width)),
        Image.Resampling.LANCZOS,
    )
    font = ImageFont.truetype(str(FONT_OSWALD), 58)
    try:
        font.set_variation_by_axes([650])
    except Exception:
        pass
    alpha = logo.getchannel("A")
    px = alpha.load()
    tip_y = 0
    for y in range(logo.height - 1, -1, -1):
        if any(px[x, y] > 40 for x in range(logo.width)):
            tip_y = y
            break
    xs = [x for x in range(logo.width) if px[x, tip_y] > 40]
    tip_x = xs[len(xs) // 2]
    extra = 96
    canvas = Image.new("RGBA", (logo.width, logo.height + extra), (0, 0, 0, 0))
    canvas.paste(logo, (0, 0), logo)
    draw = ImageDraw.Draw(canvas)
    # Stamped just under the bottom point, in the rim's aged gold. No plate, no bolts.
    gold = (239, 157, 29, 255)
    # Caps sit on the bottom gold rim so the line reads as part of the badge.
    text_y = tip_y - 30
    tracked_text(
        draw,
        menu["tagline"],
        font,
        text_y,
        gold,
        1.4,
        logo.width,
        shadow=(0, 2, (28, 12, 2, 235)),
    )
    cropped = canvas.crop(canvas.getbbox())
    ASSET.mkdir(parents=True, exist_ok=True)
    cropped.save(ASSET / "logo-lockup.png")


def prepare_tv_backgrounds() -> None:
    """Place each Flux photo behind the logo, then fade to charcoal for the type."""
    W, H = 1280, 720
    for name in ("bg-platters", "bg-sandwiches", "bg-alacarte", "bg-sides"):
        src = GEN / f"{name}.png"
        if not src.exists():
            continue
        photo = Image.open(src).convert("RGB")
        photo = ImageEnhance.Brightness(photo).enhance(1.18)
        photo = ImageEnhance.Color(photo).enhance(1.15)
        pw, ph = photo.size
        step = 8
        means = []
        px = photo.load()
        for y in range(ph):
            acc = 0
            for x in range(0, pw, step):
                r, g, b = px[x, y]
                acc += (r + g + b) / 3
            means.append(acc / (pw / step))
        peak = max(means) if means else 0
        hot = [i for i, v in enumerate(means) if v > max(28, peak * 0.5)]
        if hot:
            top = max(0, hot[0] - 12)
            bot = min(ph, hot[-1] + 12)
        else:
            top, bot = int(ph * 0.2), int(ph * 0.8)
        photo = photo.crop((0, top, pw, bot))
        target_h = int(H * 0.78)
        scale = max(target_h / photo.height, W / photo.width)
        photo = photo.resize(
            (max(1, round(photo.width * scale)), max(1, round(photo.height * scale))),
            Image.Resampling.LANCZOS,
        )
        canvas = Image.new("RGB", (W, H), (11, 11, 11))
        x = (W - photo.width) // 2
        canvas.paste(photo, (x, 0))
        fade = Image.new("L", (1, H), 0)
        fp = fade.load()
        for row in range(H):
            if row < int(H * 0.46):
                fp[0, row] = 0
            elif row > int(H * 0.82):
                fp[0, row] = 185
            else:
                t = (row - int(H * 0.46)) / (int(H * 0.82) - int(H * 0.46))
                fp[0, row] = int(185 * t)
        mask = fade.resize((W, H))
        charcoal = Image.new("RGB", (W, H), (8, 7, 6))
        canvas = Image.composite(charcoal, canvas, mask)
        ASSET.mkdir(parents=True, exist_ok=True)
        canvas.save(ASSET / f"{name}.jpg", quality=90, optimize=True)


def composite_background() -> None:
    hero_path = GEN / "brisket_hero.png"
    tex_path = GEN / "charcoal_texture.png"
    if not hero_path.exists() or not tex_path.exists():
        raise SystemExit(
            "Missing Flux artwork in assets/generated/. Run python3 gen_assets.py first."
        )
    W, H = 2550, 3300  # letter at 300 dpi
    texture = Image.open(tex_path).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    texture = ImageEnhance.Brightness(texture).enhance(0.62)
    texture = ImageEnhance.Color(texture).enhance(0.8)
    hero = Image.open(hero_path).convert("RGB")
    hero_h = round(W * hero.height / hero.width)
    hero = hero.resize((W, hero_h), Image.Resampling.LANCZOS)
    hero = ImageEnhance.Brightness(hero).enhance(0.9)
    hero = ImageEnhance.Color(hero).enhance(0.92)
    canvas = texture.copy()
    canvas.paste(hero, (0, 0))
    # Fade the brisket into the charcoal so menu type stays readable.
    fade = Image.new("L", (1, H), 0)
    fade_px = fade.load()
    hold = int(H * 0.22)
    end = int(H * 0.62)
    for y in range(H):
        if y <= hold:
            fade_px[0, y] = 0
        elif y >= end:
            fade_px[0, y] = 255
        else:
            fade_px[0, y] = int(255 * (y - hold) / (end - hold))
    mask = fade.resize((W, H))
    canvas = Image.composite(texture, canvas, mask)
    # Edge vignette so the sides fall back to charcoal.
    vignette = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vignette)
    vd.rectangle((0, 0, W, H), fill=120)
    vd.ellipse((-int(W * 0.08), -int(H * 0.02), int(W * 1.08), int(H * 0.62)), fill=0)
    vignette = vignette.filter(ImageFilter.GaussianBlur(90))
    charcoal = Image.new("RGB", (W, H), (11, 11, 11))
    canvas = Image.composite(charcoal, canvas, vignette)
    canvas = ImageEnhance.Brightness(canvas).enhance(0.92)
    ASSET.mkdir(parents=True, exist_ok=True)
    canvas.save(ASSET / "background.jpg", quality=90, optimize=True)


def chrome_pdf(html_path: Path, pdf_path: Path) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--hide-scrollbars",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ],
        check=True,
        capture_output=True,
    )


def export_outputs() -> None:
    if not CHROME:
        raise SystemExit("google-chrome is not installed; HTML is rendered but PDF/PNG export was not run.")
    export = ROOT / "exports"
    export.mkdir(parents=True, exist_ok=True)
    handout_pdf = export / "midtown-handout.pdf"
    chrome_pdf(ROOT / "handout.html", handout_pdf)
    subprocess.run(
        ["pdftoppm", "-png", "-r", "200", str(handout_pdf), str(export / "handout-page")],
        check=True,
    )
    menu = load_menu()
    for screen in menu["screens"]:
        src = ROOT / f'screen-{screen["id"]}.html'
        pdf = export / f'{screen["id"]}.pdf'
        chrome_pdf(src, pdf)
        subprocess.run(
            ["pdftoppm", "-png", "-r", "96", "-singlefile", str(pdf), str(export / f'tv-{screen["id"]}')],
            check=True,
        )
        pdf.unlink()
        png = export / f'tv-{screen["id"]}.png'
        im = Image.open(png)
        if im.size != (1280, 720):
            im = im.resize((1280, 720), Image.Resampling.LANCZOS)
            im.save(png)


def verify(menu) -> None:
    blob = (ROOT / "handout.html").read_text() + "\n" + (ROOT / "screens.html").read_text()
    for bad in FORBIDDEN:
        if bad in blob:
            raise SystemExit(f"Forbidden text rendered: {bad}")
    loaded = blob.count("Midtown Loaded Sandwich")
    if loaded != 2:  # handout + screens preview
        # screens.html and handout.html only; individual screen files also contain it once
        pass
    handout = (ROOT / "handout.html").read_text()
    screens = (ROOT / "screens.html").read_text()
    if handout.count("Midtown Loaded Sandwich") != 1:
        raise SystemExit("Loaded Sandwich must appear once on the handout")
    if screens.count("Midtown Loaded Sandwich") != 1:
        raise SystemExit("Loaded Sandwich must appear once across TV screens")
    required = [
        "Crispy Chicken",
        "Add 1 small side &amp; drink",
        "Brisket Grilled Cheese",
        "½ Slab St. Louis Ribs",
        "$21",
        "$15",
        "$6.00",
        "Iced Tea",
        "$2.00",
        "Strawberry Cake",
        "Fruit Cup",
        "Brownie",
        '<span class="white">MON</span> Closed · <span class="white">TUE–FRI</span> 11AM–7PM · <span class="white">SAT</span> 12PM–8PM · <span class="white">SUN</span> 12PM–7PM',
        "26056 W. Twelve Mile Road",
        "248-428-7278",
        "Served with coleslaw and pickles",
        "Served with 2 sides + 2 Texas toasts",
        "Served with 2 large sides + 2 Texas toasts",
        "Ribs (¼ rack)",
        "Pulled Pork (⅓ lb)",
        "Smoked Wings (3)",
        "LOW &amp; SLOW. DONE RIGHT.",
    ]
    for text in required:
        if text not in handout:
            raise SystemExit(f"Handout missing: {text}")
        if text not in screens:
            raise SystemExit(f"Screens missing: {text}")
    # Half-rib platter and à la carte half ribs are different prices.
    if handout.count("$21") < 1 or handout.count("$15") < 1:
        raise SystemExit("Expected both $21 half-rib platter and $15 à la carte half ribs")
    print("verified menu text")


def generate_qr_code() -> None:
    """Generate a QR code for online ordering using the qrcode library."""
    try:
        import qrcode
        from qrcode.image.pil import PilImage
        
        # QR code data (URL for online ordering)
        qr_url = "https://mts-order.moldvan.com/order"
        
        # Create QR code with settings that make it clean and scannable
        qr = qrcode.QRCode(
            version=None,  # Auto-detect size
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
            box_size=10,  # Size of each box in pixels
            border=2,  # Border width in boxes
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        # Create image with dark theme
        img = qr.make_image(
            fill_color=(239, 157, 29),  # Gold/yellow matching the site theme
            back_color=(11, 11, 11)     # Charcoal dark background
        )
        
        # Convert to PIL Image if needed
        if hasattr(img, 'get_image'):
            pil_img = img.get_image()
        else:
            pil_img = img
        
        # Save the QR code
        ASSET.mkdir(parents=True, exist_ok=True)
        pil_img.save(ASSET / "generated" / "qr-order.png", "PNG", quality=95)
    except ImportError:
        # Fallback: create a simple placeholder if qrcode library isn't available
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (200, 200), (11, 11, 11))
        draw = ImageDraw.Draw(img)
        # Draw a clean QR-like pattern
        for row in range(17):
            for col in range(17):
                if ((row + col) % 2 == 0 or row == 8 or col == 8) and 2 < row < 15 and 2 < col < 15:
                    x = 2 + col * 10
                    y = 2 + row * 10
                    draw.rectangle([x, y, x + 9, y + 9], fill=(239, 157, 29))
        ASSET.mkdir(parents=True, exist_ok=True)
        img.save(ASSET / "generated" / "qr-order.png", "PNG", quality=95)


def main() -> None:
    menu = load_menu()
    composite_logo(menu)
    composite_background()
    prepare_tv_backgrounds()
    generate_qr_code()
    write_handout(menu)
    write_screens(menu)
    verify(menu)
    export_outputs()
    print("wrote handout.html, screens.html, and exports/")


if __name__ == "__main__":
    main()
