# Midtown Smokehouse handout — OpenCode continuation

Updated: October 25, 2026

Read this before editing `mts/handout/`. The original design brief is `mts/continue.md`. Confirmed prices in that file and in `menu.json` win over older site or CMS prices. This folder does not change the marketing site or `mts/data/menu.json`.

## What is already done

Published at https://mts.moldvan.com/handout/ (index, `handout.html`, `screens.html`, PDF, page PNGs, four TV PNGs). CloudFront can serve a stale copy; hard-refresh.

- Two-sided US Letter portrait handout. Shared logo on the left, address and phone on the right, one shared brisket background, hours in the same full-width footer on both pages.
- Four 1280×720 TV screens. Not six. There are only four TVs.
- Logo lockup: the original fork handle is continued past the center flame so the hole sits on the top of the D in MIDTOWN. `LOW & SLOW` and `DONE RIGHT` are stamped along the shield's outer chevron edge, each letter rotated to the local angle, in aged gold. A stylized semi-transparent gold plate follows the V-shape behind the text, with a gold star at the V junction.
- Each TV has its own Flux food photo. The logo is large and sits on that photo. Section headers and items use the site’s heavy sans and drop shadow. Hours are only on screens 1 and 3. Address and phone are only on screens 2 and 4.

Do not undo those footer rules. `README.md` still says hours are on every TV screen and that nothing is deployed. That is stale. The print handout still has address and hours on both pages.

## What changed this session (Oct 25, 2026) — in `build.py`

`write_handout()` page-1 previously rendered three `.col` divs inside a 2-column grid, so Wings + Desserts wrapped under the left column and bled off the right edge. Now:

- Page-1 has exactly 2 columns. Right column contains the Quesadilla + Crazy Potato side-by-side row, then Whole Wings and Desserts stacked underneath (not in a row with them).
- `#page-1 .mast` is its own dark bar (`background: rgba(8,7,6,0.85)`, padding, border-radius) so the header is separated from the photo background — the header is no longer enclosed in the photo.
- Quesadilla/Crazy Potato side-sections: header (`section-head`) sits clear at top with NO photo behind it. The background image (`section-bg-img`) sits behind `.side-photo` only (the note text), dimmed via `filter: brightness(0.5)` on the image element only — not on the whole section element, so text stays at full brightness.
- Supporting CSS added: `#page-1 .side-section .side-photo`, `.section-bg-img`, `.side-photo > p`.

## Do not

- Run `mts/deploy.sh`. It syncs the whole bucket with `--delete` and must not wipe CMS `data/menu.json`. Publish only the handout prefix instead (see "Publish").
- Echo `mts/.deploy.env` or `~/.wp-app-password`.
- Print unconfirmed items, `$0.00`, “closing time to confirm”, a trailing dot after BEVERAGES or DESSERTS, or the old desserts (jalapeño corn bread, Meat Sampler, strawberry banana / lemon cakes).
- Replace `logo_flux.png` with `tagline_words.png`. That Flux pass dropped SLOW and restyled DONE. It was not used.
- Put the tagline back on a rectangular plate. The user rejected that as bolted on.
- Flatten the logo onto black. The lockup must stay RGBA with transparent corners. Saving an RGB intermediate and converting it made a black box behind the logo once already.

## Screens

| Screen | File | Columns | Footer | Background |
|---|---|---|---|---|
| 1 | `01-platters` | Platters \| Big Platters | hours | `bg-platters.jpg` |
| 2 | `02-sandwiches` | Sandwiches + Quesadilla \| Specials + Crazy Potato | address + phone | `bg-sandwiches.jpg` |
| 3 | `03-alacarte` | À la carte \| Wings + Combos | hours | `bg-alacarte.jpg` |
| 4 | `04-sides` | Sides + Catering \| Beverages + Desserts | address + phone | `bg-sides.jpg` |

Screen 4 is `"compact": true` so the address footer is not clipped. Hours string, exact:

`MON Closed · TUE–FRI 11AM–7PM · SAT 12PM–8PM · SUN 12PM–7PM`

Contact: 26056 W. Twelve Mile Road, Southfield, MI 48034, 248-428-7278.

## Type

Print pages use Oswald + DM Sans from `fonts/`. Leave that unless asked.

TV only, matching https://mts.moldvan.com/ (`mts/pages/menu.html`):

- Headers: system sans, weight 900, upright, uppercase, letter-spacing -0.04em, white, `text-shadow: 0 2px 12px rgba(0,0,0,.9)`.
- Items: sans, weight 900, italic, letter-spacing -0.03em, shadow `0 1px 8px rgba(0,0,0,.9)`.
- Prices: `#F5D000`, weight 900, italic, shadow `0 1px 8px rgba(0,0,0,.85)`.

`continue.md` said no italic section headers. The later TV request overrides that for item names and prices. TV section headers stay upright, like the site nav, not the italic section titles.

## Artwork

ComfyUI on the Spark: `http://192.168.1.205:8188` (also `spark.attlocal.net:8188`). Local weights: UNET `flux1-dev.safetensors`, DualCLIP `t5xxl_fp8_e4m3fn.safetensors` + `clip_l.safetensors` type `flux`, VAE `ae.safetensors`. Working txt2img is `gen_assets.py`: CLIPTextEncodeFlux guidance 3.5, KSampler euler/simple, cfg 1, about 20 steps. Flux.1 Dev is weak at exact text and at a textbook smoke ring.

FluxKontextProImageNode is an API node and returned `Unauthorized` here. Do not depend on it.

- Print background: `assets/generated/brisket_hero.png` (seed 20261022) plus `charcoal_texture.png`, composited by `build.py` into `assets/background.jpg`. `brisket_hero_v1.png` and `brisket_v3.png` were rejected.
- TV backgrounds: `assets/generated/bg-platters.png`, `bg-sandwiches.png`, `bg-alacarte.png`, `bg-sides.png`. `prepare_tv_backgrounds()` crops to the bright food band, scales it into the top of a 1280×720 frame, and fades the lower part for type. Output is `assets/bg-*.jpg`.
- Logo source of truth for the build is `assets/generated/logo_lockup_v2.png`. `composite_logo()` prefers it, falls back to `logo_flux.png`. A bad file there will ship.
- `build_lockup.py` produces `logo_lockup_v2.png` from `mts/brand-kit/logos/primary_logo_lockup.png`: it samples the artwork's own outer chevron edge and stamps LOW & SLOW and DONE RIGHT along that edge, each glyph rotated to the local edge angle, in the aged gold sampled from the rim. A stylized semi-transparent gold plate follows the V-shape behind the text, with a gold star at the V junction. The canvas is extended 78px so the words clear the badge. `finish_logo.py` still builds the older `logo_flux.png` (tagline inside the point) and is no longer the shipped lockup.
- `nameplate_center.png` spells LOW & SLOW / star / DONE RIGHT but is a bolted rectangle. Only the interior letters are used.

Background URLs in TV HTML must be `../assets/...`. They are substituted into `styles/menu.css`, and Chrome resolves them from that stylesheet. `url('assets/...')` 404s and the screen goes black even though the jpg is fine.

## TV screen layout rules (learned the hard way)

- `styles/menu.css` MUST keep `* { box-sizing: border-box; }` and `html, body { margin: 0; padding: 0; }`. Dropping them makes `.screen` render 1352×742 inside the 1280×720 page: the background stops covering the frame, a black band appears at the bottom, and the photo looks shifted. This is the single most likely regression — the reset is the first thing to restore.
- The photo is a `::before` pseudo layer with `inset: 0` and `opacity: 0.3`; a `::after` scrim sits above it. The logo is `::before`-independent, `position: absolute`, `top/left: 50%`, `translate(-50%, -50%)`, `z-index: 1`, `opacity: 0.3`, and sits BEHIND the type (`.columns` is `z-index: 2`). Do not raise the logo's z-index.
- The hours footer is generated by `render_hours()` in `build.py`; the day tokens are wrapped in `<span class="white">` there. Edit `build.py`, never the generated HTML — `build.py` overwrites `screens.html`, `handout.html` and the four `screen-*.html` files on every run.
- Verify locally before deploying:
  `google-chrome --headless=new --disable-gpu --hide-scrollbars --window-size=1280,720 --screenshot=/tmp/s1.png "file://$PWD/screen-01-platters.html"`
  Then read the PNG. This catches black bands, clipped footers and z-index problems in seconds.

## Rebuild

```bash
cd mts/handout
python3 build_lockup.py  # only if the lockup should be regenerated (plate, star, tagline)
python3 build.py         # logo, backgrounds, HTML, PDF, PNG
```

`build.py` checks forbidden strings and required prices (half ribs à la carte $15 vs platter $21, large baked beans $6.00, iced tea $2.00, Loaded Sandwich once per document). Chrome prints TV pages with `@page { size: 1280px 720px }`. `pdftoppm -r 96` must stay 1280×720. A shared letter `@page` in `menu.css` clipped the TVs before; page size stays per document.

## Publish (handout prefix only — does NOT touch CMS data/menu.json)

Deployed October 25, 2026. S3 sync to s3://midtownbbq-io/handout/ complete; CloudFront invalidation I9RWD8KBH02ZPXT1KJVTVYY61E created (status InProgress).

```bash
cd mts/handout
source .deploy.env   # do not print its contents
aws s3 sync . "s3://$BUCKET/handout/" --delete \
  --exclude "*.py" --exclude "*.md" --exclude "__pycache__/*" \
  --exclude "assets/generated/*" \
  --cache-control "public,max-age=60"
aws cloudfront create-invalidation --distribution-id "$DIST_ID" --paths "/handout/*"
```

Profile default is `moldvan.com-admin`. Bucket `mts.moldvan.com`. Distribution id is `DIST_ID` in `.deploy.env`.

## Prices that have been wrong before

- Half ribs à la carte $15. Half-rib platter $21.
- Large baked beans $6.00, not $6.50.
- Iced tea $2.00.
- Crispy chicken $10. Add 1 small side & drink $4.
- Desserts: Fruit Cup $5, Carrot Cake $6, Strawberry Cake $6, Brownie $3.
- Combo meats: Smoked Wings (3), Ribs (¼ rack), Rib Tips (½ lb), Pulled Pork (⅓ lb), Pulled Chicken (½ lb), Sausage (½ lb).
- Loaded sandwich only under Specials.

`menu.json` → `unconfirmed` is not rendered.

## Known limits

- The in-shield tagline is small so it stays inside the gold point. Making it larger crosses the border.
- The stretched shield point is the original rim, scaled. It is a little soft.
- TV food is recognizable but not a perfect match to every menu item. Screen 3 includes some odd poultry shapes. Screen 4 includes a Coke can. Regen with `gen_tv.py` on the Spark if asked; it also rewrites `logo_flux.png` from a failed inpaint, so do not let that overwrite the current lockup.
- Print brisket still lacks a textbook smoke ring and thick fat cap.
