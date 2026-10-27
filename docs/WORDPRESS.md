# moldvan.com WordPress

## Auth

```bash
WP_PASS=$(tr -d ' \n' < ~/.wp-app-password)
curl -sS -u "matt:${WP_PASS}" "https://www.moldvan.com/wp-json/wp/v2/users/me"
```

Never print the app password into chat logs or commit it.

## Prep notes (password-protected)

| Role | URL |
|------|-----|
| Hub | https://www.moldvan.com/prep/ |
| Category archive | https://www.moldvan.com/category/prep/ |
| Category slug | `prep` (name: **Prep**) |

Pattern:

1. Create/update a **post** with `categories: [<Prep id>]`, `status: publish`, and `password` set (reuse hub password unless Matt asks for a new one).
2. Link it from the hub page `/prep/` (page id historically `2213`).
3. Keep posts out of the public nav when possible.

Example posts (Sep 2026 Repool):

- `/repool-consult-prep-sep24/` — pre-call SEO / stack primer
- `/repool-website-review-meeting-notes-sep24/` — Fathom meeting notes

## REST cheat sheet

```bash
# List Prep posts
curl -sS -u "matt:${WP_PASS}" \
  "https://www.moldvan.com/wp-json/wp/v2/posts?categories=$(curl -sS -u "matt:${WP_PASS}" \
    'https://www.moldvan.com/wp-json/wp/v2/categories?slug=prep' | python3 -c 'import sys,json; print(json.load(sys.stdin)[0]["id"])')"

# Create draft post
curl -sS -u "matt:${WP_PASS}" -X POST "https://www.moldvan.com/wp-json/wp/v2/posts" \
  -H 'Content-Type: application/json' \
  -d '{"title":"…","content":"…","status":"draft","slug":"…"}'

# Update page
curl -sS -u "matt:${WP_PASS}" -X POST "https://www.moldvan.com/wp-json/wp/v2/pages/<id>" \
  -H 'Content-Type: application/json' \
  -d '{"content":"…"}'
```

Yoast fields often need a manual pass in wp-admin.

## kitchen-new

```bash
ssh kitchen-new
# WP root
cd /var/www/matthewmoldvan.com/httpsdocs/wordpress
```

Uploads / media issues: ensure ownership is appropriate for Apache (historically `apache:apache` on that host).
