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


def item_row(item, headers=None, choiceNotePrefix="", name_only=False):
    name = esc(item["name"])
    if item.get("portion"):
        name += f' <span class="portion">{esc(item["portion"])}</span>'
    if name_only or (
        "price" not in item and "prices" not in item and not item.get("heads")
    ):
        return f'<div class="item name-only"><span class="name">{name}</span></div>'
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


def header_row(headers, label=None, extra_class=""):
    classes = "item heads"
    if extra_class:
        classes += f" {extra_class}"
    name = esc(label) if label else "&nbsp;"
    return (
        f'<div class="{classes}"><span class="name">{name}</span>'
        f'<span class="leaders"></span>{price_cells(headers)}</div>'
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
    # Notes that belong under the priced rows, not above them.
    note_after_items = section["title"] in ("Whole Wings", "Combos")
    if section.get("note") and not note_after_items:
        parts.append(f'<p class="note">{esc(section["note"])}</p>')
    for item in section.get("items", []):
        if item.get("heads"):
            parts.append(
                header_row(
                    item["heads"],
                    label=item.get("headsLabel"),
                    extra_class="subheads",
                )
            )
            continue
        parts.append(
            item_row(
                item,
                choiceNotePrefix=section.get("choiceNotePrefix", ""),
                name_only=section.get("namesOnly", False),
            )
        )
    for item in section.get("single", []):
        parts.append(
            item_row(
                item,
                choiceNotePrefix=section.get("choiceNotePrefix", ""),
                name_only=section.get("namesOnly", False),
            )
        )
    if section.get("offers"):
        for item in section["offers"]:
            parts.append(
                item_row(
                    item,
                    choiceNotePrefix=section.get("choiceNotePrefix", ""),
                    name_only=section.get("namesOnly", False),
                )
            )
    choice_block = []
    if section.get("choices"):
        label = section.get("choicesLabel")
        prefix = section.get("choicesLabelPrefix", "")
        if label:
            choice_block.append(f'<p class="choices-label">{esc(prefix)}{esc(label)}</p>')
        note_prefix = section.get("choiceNotePrefix", "")
        note = section.get("choiceNote")
        lis = []
        for i, c in enumerate(section["choices"]):
            if note and i == len(section["choices"]) - 1:
                lis.append(
                    f'<li>{esc(c)}<span class="choice-note nested">'
                    f"{esc(note_prefix)}{esc(note)}</span></li>"
                )
            else:
                lis.append(f"<li>{esc(c)}</li>")
        choice_block.append(f'<ul class="choices">{"".join(lis)}</ul>')
    elif section.get("choiceNote"):
        prefix = section.get("choiceNotePrefix", "")
        choice_block.append(f'<p class="choice-note">{esc(prefix)}{esc(section["choiceNote"])}</p>')
    if choice_block:
        parts.append(f'<div class="choices-block">{"".join(choice_block)}</div>')
    if note_after_items and section.get("note"):
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


def as_photo_panel(sec, sid, sec_html=None) -> str:
    """Turn a short image/hero section into a .side-section photo panel."""
    if sec_html is None:
        sec_html = render_section(sec, sid)
    img_raw = sec.get("image") or sec.get("heroImage")
    if not img_raw:
        return sec_html
    item_count = len(sec.get("items", [])) + len(sec.get("offers", []))
    if item_count > 2:
        return sec_html
    img_src = img_raw if img_raw.startswith("assets/") else f"assets/generated/{img_raw}"
    sec_html = sec_html.replace(
        f'<img class="section-image" src="{img_src}" alt="{sec["title"]}">',
        "",
    ).replace(
        f'<img class="section-hero-image" src="{img_src}" alt="{sec["title"]}">',
        "",
    )
    m = re.match(
        r'^(<section class="section"[^>]*>)(<div class="section-head">.*?</div>)(.*)</section>$',
        sec_html,
        re.S,
    )
    if m:
        open_tag, head, tail = m.group(1), m.group(2), m.group(3)
    else:
        m = re.match(
            r'^(<section class="section"[^>]*>)(<h2>.*?</h2>)(.*)</section>$',
            sec_html,
            re.S,
        )
        if not m:
            return sec_html
        open_tag, h2, tail = m.group(1), m.group(2), m.group(3)
        head = f'<div class="section-head">{h2}</div>'
    open_tag = open_tag.replace('class="section"', 'class="section side-section"', 1)
    return (
        f"{open_tag}{head}"
        f'<div class="side-photo">'
        f'<img class="section-bg-img" src="{img_src}" alt="{esc(sec["title"])}">'
        f"{tail}"
        f"</div></section>"
    )


def write_handout(menu) -> None:
    pages = []
    page_labels = {"page-1": "Front", "page-2": "Back"}
    for page in menu["handoutPages"]:
        # Default rendering
        inner = render_mast(menu) + render_columns(menu, page["columns"]) + render_hours(menu)

        # Front/back: photo panels in columns, optional bottomRow (1 = full width, 2 = paired).
        if page["id"] in ("page-1", "page-2"):
            mast = render_mast(menu)
            cols_html = []
            for col_ids in page["columns"]:
                col_parts = [as_photo_panel(menu["sections"][sid], sid) for sid in col_ids]
                cols_html.append(f'<div class="col">{"".join(col_parts)}</div>')
            columns = f'<div class="columns">{"".join(cols_html)}</div>'
            bottom_ids = page.get("bottomRow") or []
            if bottom_ids:
                full = " full" if len(bottom_ids) == 1 else ""
                cells = []
                for sid in bottom_ids:
                    sec = menu["sections"][sid]
                    cells.append(f'<div class="bottom-cell">{as_photo_panel(sec, sid)}</div>')
                bottom = f'<div class="bottom-row{full}">{"".join(cells)}</div>'
            else:
                bottom = ""
            inner = mast + columns + bottom + render_hours(menu)

        page_id = esc(page["id"])
        label = esc(page_labels.get(page["id"], page["id"]))
        pages.append(f'<div class="page-label">{label}</div>')
        pages.append(f'<article class="page" id="{page_id}">{inner}</article>')

    page_css = (
        "@page { size: letter portrait; margin: 0; }"
        "#page-1 .side-section{position:relative;color:white;display:flex;flex-direction:column;}"
        "#page-1 .side-section > *{position:relative;z-index:2;}"
        "#page-1 .side-section .side-photo{position:relative;z-index:2;flex:1;min-height:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;}"
        "#page-1 .side-section .section-bg-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:brightness(0.88);z-index:0;pointer-events:none;display:block;}"
        "#page-1 .side-section .side-photo::after{content:\"\";position:absolute;left:0;right:0;bottom:0;height:58%;background:linear-gradient(to top,rgba(0,0,0,0.72) 0%,rgba(0,0,0,0.35) 55%,transparent 100%);z-index:1;pointer-events:none;}"
        "#page-1 .side-section .side-photo > *:not(.section-bg-img){position:relative;z-index:2;}"
        "#page-1 .side-section .section-head h2{font-size:22px;padding:0;margin:0;border:0;font-family:Oswald,Impact,sans-serif;font-weight:900;text-shadow:0 2px 10px rgba(0,0,0,0.95);color:white!important;}"
        "#page-1 .side-section .side-photo > p{margin:0 0.12in;font-size:17px;line-height:1.45;max-width:92%;font-family:Oswald,Impact,sans-serif;font-weight:600;text-shadow:0 2px 10px rgba(0,0,0,0.95);color:white!important;}"
        "#page-1 .side-section .side-photo > p.choice-note{font-size:13px;font-weight:500;text-transform:none;margin-top:0.10in;}"
        "#page-1 .mast{background:transparent;padding:0.12in 0.18in;border-radius:6px;margin-bottom:0.06in;}"
        # Uniform headers (Whole Wings look). Keep font-size off .section-head so
        # .prices em columns stay aligned with item price grids.
        "#page-1 .section > h2{margin:0 0 0.07in;padding:0.08in 0 0.1em;border-bottom:2px solid var(--yellow);font-size:22px;line-height:1.05;}"
        "#page-1 .section-head{display:flex;align-items:baseline;gap:0.25em;margin:0 0 0.07in;padding:0.08in 0 0.1em;border-bottom:2px solid var(--yellow);font-size:inherit;line-height:1.05;}"
        "#page-1 .section-head h2{font-size:22px;padding:0;margin:0;border:0;line-height:1.05;}"
        "#page-1 .section-head .prices,#page-1 .item .prices{font-size:14px;flex:0 0 auto;min-width:auto;}"
        "#page-1 .columns{flex:1 1 auto;min-height:0;}"
        "#page-1 .col{justify-content:flex-start;gap:0.16in;}"
        "#page-1 .section{margin-bottom:0.04in;}"
        "#page-1 .item{margin:0.065in 0;line-height:1.35;}"
        "#page-1 .note,#page-1 .choice-note,#page-1 .detail{margin-top:0.045in;margin-bottom:0.07in;}"
        "#page-1 .item.heads.subheads{margin-top:0.12in;margin-bottom:0.07in;}"
        # Compact name-only Sides under Sandwiches (prices live on the back).
        "#page-1 #section-sidesFront{display:grid;grid-template-columns:1fr 1fr;column-gap:0.18in;row-gap:0;align-items:start;}"
        "#page-1 #section-sidesFront > h2,#page-1 #section-sidesFront > .section-head{grid-column:1 / -1;}"
        "#page-1 #section-sidesFront .item.name-only{margin:0.03in 0;line-height:1.2;}"
        "#page-1 #section-sidesFront .item.name-only .name{font-size:13px;}"
        # Shared bottom row: Crazy Potato | Quesadilla on one baseline.
        "#page-1 .bottom-row{display:grid;grid-template-columns:1fr 1fr;column-gap:0.25in;margin-top:0.10in;flex:0 0 auto;align-items:stretch;}"
        "#page-1 .bottom-cell{min-width:0;display:flex;flex-direction:column;}"
        "#page-1 .bottom-cell .side-section{flex:1;margin:0;}"
        "#page-1 #section-crazyPotato .side-photo,#page-1 #section-quesadilla .side-photo{flex:0 0 auto;min-height:1.85in;height:1.85in;max-height:1.85in;justify-content:flex-end;align-items:stretch;text-align:left;padding:0.10in 0.14in 0.10in;}"
        "#page-1 #section-crazyPotato .side-photo::before,#page-1 #section-quesadilla .side-photo::before{content:\"\";position:absolute;left:0;right:0;top:0;height:42%;background:linear-gradient(to bottom,rgba(0,0,0,0.55) 0%,transparent 100%);z-index:1;pointer-events:none;}"
        "#page-1 #section-crazyPotato .side-photo::after,#page-1 #section-quesadilla .side-photo::after{height:78%;background:linear-gradient(to top,rgba(0,0,0,0.82) 0%,rgba(0,0,0,0.50) 45%,rgba(0,0,0,0.18) 75%,transparent 100%);}"
        "#page-1 #section-crazyPotato .side-photo > p.note,#page-1 #section-quesadilla .side-photo > p.note{margin:0;max-width:none;font-size:15px!important;font-weight:700!important;font-family:\"DM Sans\",sans-serif!important;line-height:1.3;text-align:left;color:#fff!important;text-shadow:0 1px 2px rgba(0,0,0,1),0 2px 10px rgba(0,0,0,0.95),0 0 10px rgba(0,0,0,0.9)!important;}"
        "#page-1 #section-crazyPotato .side-photo .choice-note,#page-1 #section-quesadilla .side-photo .choice-note{margin:0.08in 0 0!important;max-width:none;font-size:13px!important;font-weight:700!important;font-family:Oswald,Impact,sans-serif!important;letter-spacing:0.04em;text-transform:uppercase;text-align:left!important;color:var(--yellow)!important;text-shadow:0 1px 2px rgba(0,0,0,1),0 2px 10px rgba(0,0,0,0.95),0 0 10px rgba(0,0,0,0.9)!important;}"
        # Whole Wings: priced rows over the hero; "Wings only" under them.
        "#page-1 #section-wings .side-photo{align-items:stretch;justify-content:flex-end;text-align:left;padding:0.10in 0 0.08in;min-height:1.7in;}"
        "#page-1 #section-wings .side-photo > .item{width:100%;margin:0.04em 0;padding:0 0.12in;box-sizing:border-box;}"
        "#page-1 #section-wings .side-photo > p.note{margin:0.08in 0.12in 0;max-width:none;font-size:12px!important;font-weight:700!important;font-family:\"DM Sans\",sans-serif!important;text-align:right;line-height:1.2;color:#fff!important;text-shadow:0 1px 2px rgba(0,0,0,1),0 2px 10px rgba(0,0,0,0.95),0 0 8px rgba(0,0,0,0.9)!important;}"
        # Right inset only — keep WHOLE WINGS left-aligned with other headers,
        # while 6/12/24 still match the padded item price columns.
        "#page-1 #section-wings .section-head{padding-left:0;padding-right:0.12in;box-sizing:border-box;}"
        "#page-2 .side-section{position:relative;color:white;display:flex;flex-direction:column;}"
        "#page-2 .side-section > *{position:relative;z-index:2;}"
        "#page-2 .side-section .side-photo{position:relative;z-index:2;flex:1;min-height:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;}"
        "#page-2 .side-section .section-bg-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:brightness(0.88);z-index:0;pointer-events:none;display:block;}"
        "#page-2 .side-section .side-photo::after{content:\"\";position:absolute;left:0;right:0;bottom:0;height:58%;background:linear-gradient(to top,rgba(0,0,0,0.72) 0%,rgba(0,0,0,0.35) 55%,transparent 100%);z-index:1;pointer-events:none;}"
        "#page-2 .side-section .side-photo > *:not(.section-bg-img){position:relative;z-index:2;}"
        "#page-2 .side-section .section-head h2{font-size:22px;padding:0;margin:0;border:0;font-family:Oswald,Impact,sans-serif;font-weight:900;text-shadow:0 2px 10px rgba(0,0,0,0.95);color:white!important;}"
        "#page-2 .side-section .side-photo > p{margin:0 0.12in;font-size:17px;line-height:1.45;max-width:92%;font-family:Oswald,Impact,sans-serif;font-weight:600;text-shadow:0 2px 10px rgba(0,0,0,0.95);color:white!important;}"
        "#page-2 .side-section .side-photo > p.choice-note{font-size:13px;font-weight:500;text-transform:none;margin-top:0.10in;}"
        # Uniform headers (same Whole Wings look as page 1); item rhythm matches front.
        "#page-2 .section > h2{margin:0 0 0.07in;padding:0.08in 0 0.1em;border-bottom:2px solid var(--yellow);font-size:22px;line-height:1.05;}"
        "#page-2 .section-head{display:flex;align-items:baseline;gap:0.25em;margin:0 0 0.07in;padding:0.08in 0 0.1em;border-bottom:2px solid var(--yellow);font-size:inherit;line-height:1.05;}"
        "#page-2 .section-head h2{font-size:22px;padding:0;margin:0;border:0;line-height:1.05;}"
        "#page-2 .section-head .prices,#page-2 .item .prices{font-size:14px;flex:0 0 auto;min-width:auto;}"
        "#page-2 .columns{flex:1 1 0;min-height:0;}"
        "#page-2 .col{justify-content:flex-start;gap:0.14in;}"
        "#page-2 .item{margin:0.055in 0;line-height:1.32;}"
        "#page-2 .section{margin-bottom:0;}"
        "#page-2 .section > .note{margin:0 0 0.05in;}"
        "#page-2 .item.heads.subheads{margin-top:0.12in;margin-bottom:0.07in;}"
        # Catering: 2-col keeps clearance while item spacing matches front.
        "#page-2 #section-catering{display:grid;grid-template-columns:1fr 1fr;column-gap:0.16in;align-items:start;}"
        "#page-2 #section-catering > h2,#page-2 #section-catering > .section-head,#page-2 #section-catering > .note{grid-column:1 / -1;}"
        "#page-2 #section-catering .item{margin:0.045in 0;}"
        # Full-width Combos band under both columns.
        "#page-2 .bottom-row{display:grid;grid-template-columns:1fr 1fr;column-gap:0.25in;margin-top:0.12in;flex:0 0 auto;align-items:stretch;position:relative;z-index:3;}"
        "#page-2 .bottom-row.full{grid-template-columns:1fr;}"
        "#page-2 .bottom-cell{min-width:0;display:flex;flex-direction:column;}"
        "#page-2 .bottom-cell .side-section{flex:1;margin:0;}"
        # Match Combos hero gap: yellow header rule ↔ photo ↔ hours rule.
        "#page-2 .bottom-row .section-head{margin-bottom:0.08in;}"
        "#page-2 .hours{margin-top:0.08in;}"
        # Combos: Pick 2/3 across top, meats fill middle, notes tight under list.
        "#page-2 #section-combos .section-bg-img{filter:brightness(0.88)!important;}"
        "#page-2 #section-combos .side-photo::before{content:\"\";position:absolute;left:0;right:0;top:0;height:48%;background:linear-gradient(to bottom,rgba(0,0,0,0.72) 0%,rgba(0,0,0,0.40) 45%,transparent 100%);z-index:1;pointer-events:none;}"
        "#page-2 #section-combos .side-photo::after{height:72%;background:linear-gradient(to top,rgba(0,0,0,0.75) 0%,rgba(0,0,0,0.42) 50%,rgba(0,0,0,0.15) 80%,transparent 100%);}"
        "#page-2 #section-combos .side-photo{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:auto auto auto;column-gap:0.40in;row-gap:0.12in;align-items:start;align-content:space-between;text-align:left;padding:0.12in 0.22in;min-height:1.90in;height:1.90in;max-height:1.90in;flex:0 0 auto;box-sizing:border-box;}"
        "#page-2 #section-combos .side-photo > div.item{font-size:22px;line-height:1.2;font-weight:700;}"
        "#page-2 #section-combos .side-photo > div.item .name{font-size:22px;}"
        "#page-2 #section-combos .side-photo > div.item .price{font-size:24px;}"
        "#page-2 #section-combos .side-photo > div.item:nth-of-type(1){grid-column:1;grid-row:1;width:100%;margin:0;}"
        "#page-2 #section-combos .side-photo > div.item:nth-of-type(2){grid-column:2;grid-row:1;width:100%;margin:0;}"
        "#page-2 #section-combos .side-photo > .choices-block{grid-column:1 / -1;grid-row:2;width:100%;}"
        "#page-2 #section-combos .side-photo > .choices-block > .choices{width:100%;margin:0!important;grid-template-columns:1fr 1fr 1fr;gap:0.42em 0.30in;}"
        "#page-2 #section-combos .side-photo > .choices-block > .choices li{font-size:19px;color:#fff;font-weight:700;line-height:1.2;white-space:nowrap;text-shadow:0 1px 2px rgba(0,0,0,1),0 2px 10px rgba(0,0,0,0.95),0 0 8px rgba(0,0,0,0.9);}"
        "#page-2 #section-combos .side-photo > .choices-block > .choices li .choice-note.nested{display:block;margin:0!important;padding:0.02em 0 0;white-space:normal;font-size:11px!important;font-weight:700!important;font-family:Oswald,Impact,sans-serif!important;letter-spacing:0.02em;text-transform:uppercase;color:var(--yellow)!important;text-align:left!important;line-height:1.05;text-shadow:0 1px 2px rgba(0,0,0,1),0 2px 10px rgba(0,0,0,0.95),0 0 8px rgba(0,0,0,0.9)!important;}"
        "#page-2 #section-combos .side-photo > p.note{grid-column:1 / -1;grid-row:3;justify-self:start;margin:0;max-width:none;font-size:13px!important;font-weight:700!important;font-family:\"DM Sans\",sans-serif!important;text-align:left;line-height:1.2;text-transform:none;letter-spacing:0;color:#fff!important;text-shadow:0 1px 2px rgba(0,0,0,1),0 2px 10px rgba(0,0,0,0.95),0 0 8px rgba(0,0,0,0.9)!important;}"
        # Screen-only Front/Back labels — hide in print so they don't create blank PDF pages.
        ".page-label{color:var(--yellow);font-family:Oswald,Impact,sans-serif;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;font-size:20px;margin:0 0 0.12in 0;text-shadow:0 2px 8px rgba(0,0,0,0.9);}"
        "@media print{.page-label{display:none!important;}}"
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
    for stale in export.glob("handout-page-*.png"):
        stale.unlink()
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
