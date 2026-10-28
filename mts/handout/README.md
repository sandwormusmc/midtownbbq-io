# Midtown Smokehouse — printed handout and TV menus

Two-sided US Letter portrait handout and 1280×720 TV screens. Menu copy and prices come from `menu.json`. The confirmed restaurant prices in `../continue.md` are the source. This folder does not change the live marketing site or `mts/data/menu.json`.

Nothing here changes the live marketing site or `mts/data/menu.json`. The handout deploys to `s3://midtownbbq-io/handout/` and serves at https://midtownbbq.io/handout/ via CloudFront (`E293E6RVQ0BLMD`).

## Layout

- Print size is US Letter portrait. No other trim size was specified. Critical type stays inside about 0.3 in of the page edge.
- Both pages share one logo file (`assets/logo-lockup.png`) at the same size, on the left, with the address and phone on the right.
- Both pages share one background (`assets/background.jpg`).
- Hours sit in the same full-width footer on every page and TV screen: `MON Closed · TUE–FRI 11AM–7PM · SAT 12PM–8PM · SUN 12PM–7PM`.
- Section headings are upright bold condensed (Oswald), white, with a yellow rule and a dark drop shadow. Prices are yellow (`#F5D000`). There is no trailing dot after Beverages or Desserts.

Page 1: Sandwiches, Meat À La Carte, Sides, Quesadilla (right column top), then Crazy Potato, Whole Wings, Desserts (right column below).

Page 2: Platters, Big Platters, Combos (left column); Sides, Catering, Specials, Beverages (right column).

Four TV screens at 1280×720. Each screen has its own food photograph. The logo sits large on that photograph. Section headers and item names use the same heavy sans and drop shadow as mts.moldvan.com. Hours are on screens 1 and 3. Address and phone are on screens 2 and 4.

1. Platters and big platters
2. Sandwiches, quesadilla, specials, crazy potato
3. À la carte, wings, and combos
4. Sides, catering, beverages, and desserts

- Hero and charcoal texture are generated with Flux.1 Dev on the DGX Spark ComfyUI (`http://192.168.1.205:8188`) via `gen_assets.py`.
- `build.py` composites them into one background: brisket across the top, fading into the charcoal wood texture so menu type stays readable.
- The wordmark is the primary logo. The fork handle is the original utensil, continued past the flame so the hole sits on the top of MIDTOWN. `LOW & SLOW` and `DONE RIGHT` are the Flux.1 Dev gold letters and star, stamped inside the shield’s lower point. There is no separate plate. TV food photographs are Flux.1 Dev on the DGX Spark (`gen_tv.py`).
- The brisket render used on the pages has a dark peppered crust and sliced beef on a black tray. Flux still paints the cut face pinker than a classic tan slice with a thin smoke ring and a thick fat cap. A later pass (`assets/generated/brisket_v3.png`) was not used: the interior looked artificial and a green garnish appeared. Run `python3 gen_assets.py brisket` and then `python3 build.py` for another pass.

## Rebuild and export

```bash
cd mts/handout
python3 gen_assets.py   # Spark / Flux; several minutes
python3 build.py        # logo, background, HTML, PDF, PNG
```

Preview in a browser:

- `handout.html` — two letter pages
- `screens.html` — all four TV screens

Exports land in `exports/`:

- `midtown-handout.pdf` — print file (vector type)
- `handout-page-1.png`, `handout-page-2.png` — 200 dpi page previews
- `tv-01-platters.png` through `tv-04-sides.png` — 1280×720

## Not on the menu

`menu.json` → `unconfirmed` lists older items that were not in the latest manual price list (priced coleslaw, jalapeño corn bread, wing platters, meat sampler, sauce and toast extras, strawberry banana / lemon cakes). They are not printed.

Descriptions marked in `continue.md` as retained from the previous draft (sausage varieties, quesadilla meats, crazy potato, platter portions, combo serving note) are included and have not been newly reconfirmed.
