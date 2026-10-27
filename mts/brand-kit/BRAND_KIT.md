# Midtown Smokehouse — Brand Kit (FB + IG pull)

**Agents: this is mandatory visual source of truth.**

## Sources pulled
- Facebook page profile (Marhabagrillfarmington → Midtown smokehouse): `logos/primary_logo_lockup.jpg`
- Instagram @midtown.s.house profile + recent posts: `logos/instagram_profile_pic.jpg`, `photos/*`, `references/instagram_profile_screenshot.png`

## Hard rules
1. **Keep the logo** — use `logos/primary_logo_lockup.jpg` / IG profile mark. Do **not** redraw, recolor, or replace the flame + crossed spatula/fork mark.
2. **Keep the color style** — charcoal/black grounds, **neon chartreuse** outline accent, **flame orange/red**, banner yellow, white type.
3. **Keep the type feel** — heavy distressed display for MIDTOWN; tracked small-caps sans for SMOKEHOUSE; clean UI sans for product UI.

## Color tokens
| Token | Hex | Use |
|-------|-----|-----|
| bg_charcoal | `#0B0B0B` | Page background |
| bg_surface | `#161412` | Cards/surfaces |
| neon_chartreuse | `#D6FF2A` | Logo outline / sharp accents |
| flame_orange | `#FF5F00` | CTAs, flame, emphasis |
| flame_red | `#E12600` | Gradient accents |
| banner_yellow | `#FFCC00` | Location/chips banners |
| logo_white | `#FFFFFF` | Primary type on dark |
| cream | `#F3E6D0` | Soft body text alternate |
| smoke_gray | `#8A8478` | Muted meta |

## Typography
- **Display:** Match logo MIDTOWN (heavy, condensed, distressed). Prefer compositing the logo asset over faking the face.
- **Subbrand:** Tracked uppercase sans for SMOKEHOUSE.
- **UI:** Inter or DM Sans.
- **Promo accents:** Bold brush/slanted sans on yellow stroke banners (see IG promos).

## Contact (from IG)
- 26056 W 12 Mile Rd, Southfield, MI 48034
- 248-428-7278
- midtownsmokehouse.com

## Files
```
brand-kit/
  BRAND_KIT.md
  BRAND_KIT.json
  logos/primary_logo_lockup.jpg
  logos/instagram_profile_pic.jpg
  logos/facebook_profile_logo.jpg
  photos/ig_promo_*.jpg
  references/instagram_profile_screenshot.png
  references/color_tokens.png
```

## UI accent (ordering app) — locked 2026-10-12
- Ordering UI highlight/price accent: **yellow `#F5D000`** (replaces neon chartreuse `#D6FF2A` in hi-fi HTML).
- Primary CTA remains flame orange `#FF5F00`.
- Hero photo presentation: background + vignette on all screens — see `../VISUAL_DIRECTION.md` or company `design-preview/VISUAL_DIRECTION.md`.
