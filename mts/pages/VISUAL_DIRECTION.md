# Midtown Smokehouse — Visual Direction (locked 2026-10-12)

**Authority:** Matt Moldvan (human board feedback) via Cursor session.  
**Live preview:** http://192.168.1.205:3101/ (hard-refresh after changes)  
**Tracked on:** MID-10 (Phase 2b revision)

## Accent color
| Token (CSS class name) | Was | Now | Use |
|---|---|---|---|
| `text-chartreuse` / `bg-chartreuse` / `border-chartreuse` | `#D6FF2A` (neon chartreuse) | `#F5D000` (yellow) | highlights, prices, checkmarks, success accents |
| `flame_orange` / `bg-orange` | `#FF5F00` | `#FF5F00` (unchanged) | primary CTAs |

Keep class names for now (avoid mass rename churn); values are yellow.

## Hero photography
- **File:** `brand-kit/photos/hero_smoked_meats.jpg`
- **Generator:** ComfyUI Flux.1 Dev on Spark (`127.0.0.1:8188`)
- **Do not use:** bread, toast, sandwiches, pastry, beef wellington, people, hands, influencer faces
- **Why:** Earlier RealVisXL hero had a surreal toast-with-meat-embedded slice (“toast wellington”). Backup: `hero_smoked_meats.toast-bak.jpg`

## Hero presentation (all screens)
- **Not** a separate rounded image block on Home.
- Every `.mobile-frame` has:
  - `.mobile-bg` — pinned full-bleed `hero_smoked_meats.jpg` (`brightness(0.55)`, slight desaturate)
  - `.mobile-vignette` — four-edge fade into charcoal (top/bottom/left/right)
  - `.mobile-scroll` — content above layers
- Cards/headers use `.bg-surface-glass` ≈ `rgba(22,20,18,0.94)` so type stays readable and the food stays atmospheric (not the focal point).

## Per-screen imagery (still required)
| Screen | Imagery |
|---|---|
| Home | Background hero only + logo; headline + Start Order |
| Menu | Thumb photos per row (`menu_*.jpg`) |
| Item detail | Product full-bleed (`detail_brisket.jpg`) over shared bg |
| Cart | Line-item thumbs |
| Checkout / Confirm | Shared bg + glass panels |

## Paths
- Company preview: `~/.paperclip/companies/midtown-smokehouse/design-preview/`
- Designer workspace mirror: `~/.openclaw/workspace-midtown-designer/design-preview/`
- Brand kit photos: `brand-kit/photos/` (synced both places)

## HTML hygiene
- No Markdown/LaTeX (`$\rightarrow$`, `**bold**`) in HTML — Unicode / real tags only.

## Logo (locked 2026-10-12)
- **Home (Start Order):** true transparent PNG `primary_logo_lockup.png` (BiRefNet/rembg cutout), width `calc(100% - 40px)` / **20px** L/R margin. No screen-blend hack.
- **Other screens:** `primary_logo_lockup_sm.png`.
- Also available: `_md.jpg`, source copy `source_attachment_799b1642.jpg`, previous `primary_logo_lockup.old.jpg`.
- Do not revert to the old square Facebook crop for Home.

## Home vs subpage background
- **Home** (`.mobile-frame--home`): brighter hero (`brightness ~0.82`) + lighter vignette so food takes more center stage.
- **Other screens**: dimmer hero (`brightness ~0.55`) + heavier vignette so UI/cards stay readable.
