# Midtown Smokehouse — marketing site

**Live:** https://mts.moldvan.com/  
**Ordering SPA:** https://mts-order.moldvan.com/  
**Menu CMS:** https://mts.moldvan.com/admin/

Static marketing pages (home, menu, about, location, catering) plus a small password-protected CMS that publishes `data/menu.json`.

## Deploy
```bash
export AWS_PROFILE=moldvan.com-admin
./deploy.sh
```

Admin password is in `.cms-password` (local only — not deployed).
CMS API URL is in `.deploy.env` as `CMS_API_URL`.
