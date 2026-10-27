# Midtown Smokehouse — Cursor continuation

Updated: October 20, 2026

## Task

Continue the Midtown Smokehouse menu redesign.

Deliver:
1. A coordinated two-sided portrait printed handout.
2. Matching 1280 × 720 TV menu screens.
3. Editable source files and structured menu data.
4. Print-ready PDF and PNG exports.

The user wants rich, generated rustic barbecue artwork with clean,
readable menu typography similar to https://mts.moldvan.com/.

ChatGPT completed several visual iterations but could not finish because
its workspace and image attachments became inaccessible. The latest
requested visual changes have NOT been completed.

Inspect the repository and available references, then begin implementation.
Do not stop at a proposal. Preserve unrelated work. Do not deploy or
publish without authorization.

## Source priority

The manually typed restaurant prices in this document supersede earlier
online prices and generated menu drafts.

Never print ordering-site $0.00 option placeholders as actual prices.
Never overwrite these confirmed prices based on older generated artwork.

Descriptions and portion details explicitly marked as retained from the
previous draft have not been newly reconfirmed.

## Public references

Website:
https://mts.moldvan.com/

Primary logo:
https://mts.moldvan.com/brand-kit/logos/primary_logo_lockup.png

Hero background:
https://mts.moldvan.com/brand-kit/photos/hero_smoked_meats.jpg

Ordering site — secondary reference only:
https://midtownsmokehousebbq0188.s4shops.com/

If this workspace contains the website repository, inspect its existing
brand-kit assets, fonts, colors, and CSS first. Otherwise download and
inspect the public logo and hero files.

Earlier ChatGPT retrieval failures do not establish that the URLs are broken.

## Required design changes

1. Use the SAME logo asset, size, proportions, colors, and position on
   both handout pages.

2. Base the logo on the supplied primary logo reference. Correct the
   utensils above it into one recognizable barbecue spatula and one
   barbecue fork, with coherent handles and prongs.

3. Keep MIDTOWN straight rather than curved or arched. Remove bolts and
   rivets. Preserve natural proportions without vertical stretching
   or squashing.

4. Integrate LOW & SLOW. DONE RIGHT. as a small stamped extension beneath
   the bottom rim of the logo. Match the logo's material, texture, and
   colors. It must not look like a separate plate bolted onto the logo.

5. Place the logo on the LEFT of the header, with the address and phone
   on the RIGHT.

6. Use the SAME background artwork on both handout pages.

7. Regenerate the hero food using the supplied image as a style reference,
   but make it unmistakably smoked brisket: dark pepper bark, moist sliced
   beef grain, rendered fat, and a subtle pink smoke ring.

8. Keep the hero and texture subdued behind text. Readability matters.

9. Move business hours OUT of the menu columns and into identical compact
   full-width footers on both pages.

10. Normalize the palette to the website and reference assets:
    charcoal, cream/white, yellow emphasis, aged gold, and appropriate
    existing logo accents.

11. Use upright bold condensed section headings with white/yellow
    treatment and subtle dark drop shadows, matching the website.
    No italic section headers.

12. No trailing dot after BEVERAGES or DESSERTS.

13. Reduce excessive footer margins and use the available vertical space,
    while retaining clear gutters and comfortable text spacing.

14. Use these shortened serving notes:
    - Sandwiches: Served with coleslaw and pickles
    - Platters: Served with 2 sides + 2 Texas toasts
    - Big Platters: Served with 2 large sides + 2 Texas toasts

The user rejected basic-looking earlier layouts and explicitly requested
generated imagery. Use image generation for artwork if available.

For accurate spelling and prices, render menu text separately as editable
HTML/CSS or vector text over the shared artwork. Do not bake the entire
menu into a generated background.

If image generation is unavailable, complete the content and layout using
the supplied artwork as a clearly identified temporary reference. Do not
claim the brisket or utensil regeneration is complete.

## Contact details

26056 W. Twelve Mile Road
Southfield, MI 48034
248-428-7278

Place these to the right of the logo on both pages, outside menu columns.

## Confirmed hours

Monday: Closed
Tuesday–Friday: 11 AM–7 PM
Saturday: 12 PM–8 PM
Sunday: 12 PM–7 PM

Compact footer:
MON Closed · TUE–FRI 11AM–7PM · SAT 12PM–8PM · SUN 12PM–7PM

Remove all obsolete "closing time to confirm" notes.

## Confirmed menu

All prices below were manually supplied by the user from the restaurant.

### Catering — ½ sheet

| Item | Price |
|---|---:|
| Mac & Cheese | $35 |
| Baked Beans | $35 |
| Collard Greens | $35 |
| Sweet Corn | $30 |
| Potato Wedges | $30 |

### Specials

| Item | Price |
|---|---:|
| Brisket Grilled Cheese | $12 |
| Brisket Mac & Cheese | $12 |
| Tips & Wings (6) | $20 |
| Midtown Loaded Sandwich | $16 |

Tips & Wings:
Smoked or Fried, with 1 lb Rib Tips.

Midtown Loaded Sandwich:
Brisket, Pulled Pork & Sausage.

The user typed "Brisket Grilled & Cheese"; the established item name is
Brisket Grilled Cheese.

Place the Loaded Sandwich under Specials once, avoiding duplication.

### Sandwiches

Served with coleslaw and pickles.

| Item | Price |
|---|---:|
| Sliced or Chopped Brisket | $12 |
| Pulled Pork | $10 |
| Pulled Chicken | $10 |
| Crispy Chicken | $10 |
| Sausage Sandwich | $10 |
| Add 1 small side & drink | $4 |

Sausage choices retained from the previous menu:
Jalapeño Cheese · Polish · Beef

### Quesadilla — $10

Meat choices retained from the previous menu:
Pulled Pork · Brisket · Pulled Chicken

### Crazy Potato — $14

Description retained from the previous menu:
Potato topped with mac & cheese, baked beans, and sour cream, with choice
of beef brisket, pulled pork, or pulled chicken.

### Meat À La Carte

| Item | ½ lb | 1 lb |
|---|---:|---:|
| Beef Brisket | $14 | $26 |
| Pulled Chicken | $9 | $16 |
| Rib Tips | — | $12 |
| Pulled Pork | $9 | $16 |
| Brisket Blackened | $16 | $30 |
| Sausage | $9 | $15 |

| Item | Half | Full |
|---|---:|---:|
| Smoked Chicken | $12 | $20 |
| St. Louis Style Ribs | $15 | $28 |

IMPORTANT:
Half ribs à la carte are $15, not the old draft's $20.
The half-rib PLATTER is separately priced at $21.

### Whole Wings

| Preparation | 6 | 12 | 24 |
|---|---:|---:|---:|
| Fried | $10 | $18 | $32 |
| Smoked | $12 | $20 | $35 |

These are wings-only prices.

### Platters

Served with 2 sides + 2 Texas toasts.

| Item | Price |
|---|---:|
| Beef Brisket | $24 |
| Half Smoked Chicken | $18 |
| ½ Slab St. Louis Ribs | $21 |
| Rib Tips | $17 |
| Pulled Pork | $15 |
| Pulled Chicken | $15 |
| Smoked Sausage | $17 |

Portions retained from the earlier draft:
- Beef brisket: ½ lb
- Pulled pork: ½ lb
- Pulled chicken: ½ lb
- Smoked sausage: ½ lb
- Rib tips: 1 lb

### Big Platters

Served with 2 large sides + 2 Texas toasts.

| Item | Price |
|---|---:|
| Whole Smoked Chicken | $26 |
| Whole St. Louis Slab of Ribs | $36 |
| Rib Tips | $25 |
| Brisket | $35 |
| Pulled Pork | $20 |

Portions retained from the earlier draft:
- Rib tips: 2 lb
- Brisket: 1 lb
- Pulled pork: 1 lb

### Combos

Pick 2: $24
Pick 3: $30

Serving note retained from the earlier draft:
Served with 2 small sides and 1 Texas toast.

Preserve exactly these six meat selections:
- Smoked Wings (3)
- Ribs (¼ rack)
- Rib Tips (½ lb)
- Pulled Pork (⅓ lb)
- Pulled Chicken (½ lb)
- Sausage (½ lb)

Sausage choices:
Jalapeño Cheese · Polish · Beef

Earlier image generations incorrectly omitted ribs and duplicated sausage
varieties as separate combo selections. Avoid repeating this.

### Sides

| Item | Small | Large |
|---|---:|---:|
| Mac & Cheese | $4.50 | $6.50 |
| Sweet Corn | $4.50 | $6.50 |
| Collard Greens | $4.50 | $6.50 |
| Baked Beans | $4.50 | $6.00 |
| Potato Wedges | $5.00 | $7.00 |

Corn Bread: $2.50

IMPORTANT:
Large baked beans are $6.00, not $6.50.

### Beverages

| Item | Price |
|---|---:|
| Soda, 12 oz | $1.50 |
| Soda, 2 L | $4.00 |
| Iced Tea | $2.00 |
| Water, 16 oz | $1.50 |
| Jarritos, 12.5 oz | $2.50 |
| Root Beer, 12 oz | $2.50 |

IMPORTANT:
Iced tea is $2.00, superseding the earlier online price of $2.50.

### Desserts

| Item | Price |
|---|---:|
| Fruit Cup | $5 |
| Carrot Cake | $6 |
| Strawberry Cake | $6 |
| Brownie | $3 |

Use this current four-item selection.
Include Fruit Cup and Brownie despite earlier online sold-out labels.
Strawberry Cake is $6, not $7.

## Older entries absent from the latest manual list

Keep these in the project record as unconfirmed. Do not silently treat
their old prices or availability as currently confirmed.

Proceed with the confirmed menu above without blocking layout work.

- Coleslaw as a separately priced side:
  Old draft $4.50 small / $6 large.
  Coleslaw remains explicitly included with sandwiches.

- Jalapeño Cheese Corn Bread:
  Old draft $2.99.

- Wing platters:
  Old draft 6 fried $17 / 6 smoked $19.

- Midtown Meat Sampler:
  Old draft $55.
  ½ lb brisket, ½ lb pulled pork, 1 lb rib tips, ½ slab ribs,
  ½ lb mixed sausage, 3 smoked wings.

- Extras:
  Old draft BBQ sauce 4 oz $0.75; BBQ sauce 16 oz $6.50;
  Texas toast $0.75.

- Strawberry Banana Cake and Strawberry Lemon Cake:
  Replaced by the current four-item dessert selection.

## Existing visual artifacts

The following files exist in ChatGPT, but Cursor will need actual copies.
Do not assume ChatGPT Library IDs or scratch paths are accessible in Cursor.

Priority reference files:
- logo.png
- old-hero.png
- image(20261020-172423).png
- image(20261020-172524).png
- midtown-current-menu-left(3).jpg
- midtown-current-menu-right(3).jpg
- midtown-current-menu-specials(3).jpg

The two timestamped PNGs are the latest generated portrait handout pages.
Inspect them to confirm their page identity and layout.

Earlier supporting files:
- midtown-handout-1.png
- midtown-handout-2.png
- image(20261020-172607).png
- image(20261020-172612).png

The public URLs provide the logo and hero references independently of
ChatGPT attachments.

The restaurant photos are useful visual references, but the user's manual
transcription in this document is the authoritative pricing input.

If the latest generated pages are unavailable, proceed from this brief
and the public branding assets. Identify the layout as reconstructed.

## Implementation

Adapt to the existing repository and its conventions.

Suggested structure if no relevant project exists:

content/menu.json
assets/
handout.html
screens.html
styles/
exports/
README.md

Store menu content, portions, prices, contact details, and hours centrally.
Render print and TV layouts from the same data to avoid inconsistencies.

Use shared header/footer components and shared artwork so both handout
pages match exactly. Preserve logo aspect ratio.

Use US Letter portrait provisionally if no existing print size is specified.
Document this assumption and retain safe margins for critical content.

Suggested handout category distribution, adjustable for readability:

Page 1:
Platters, Big Platters, Combos, Sides, Catering, Beverages.

Page 2:
Sandwiches, Specials, Quesadilla, Crazy Potato, À La Carte, Wings, Desserts.

Use enough TV screens to keep text readable at 1280 × 720. Do not squeeze
the entire printed menu onto one screen. Match the handout branding.

## Required outputs

1. Editable source and structured menu content.
2. Two-page handout PDF.
3. Separate PNG previews of both handout pages.
4. 1280 × 720 PNGs for each TV menu screen.
5. README with preview/export instructions and any remaining limitations.

Do not publish changes to the live website without authorization.

## Verification

- Compare every displayed price with the confirmed tables.
- Check for duplicate items and omissions.
- Check half/full versus ½ lb/1 lb labels.
- Confirm $15 half ribs à la carte versus $21 half-rib platter.
- Confirm $6 large baked beans.
- Confirm $2 iced tea.
- Confirm $6 strawberry cake.
- Include Crispy Chicken.
- Include the $4 side-and-drink add-on.
- Use the current four-item dessert selection.
- Confirm the footer hours and remove obsolete uncertainty notes.
- Verify identical logo and background assets on both handout pages.
- Check exported print pages and TV screens for clipping, overlap,
  wrapping, contrast, and actual-size readability.

## Working preferences

Apply authorized revisions directly without repeated confirmation requests.
Preserve previously approved details.

Do not claim inaccessible references were inspected.
Do not claim image generation or exports were completed when they were not.

Complete all useful implementation work before asking about unresolved
details. Keep progress updates concise and focused on actual results.
