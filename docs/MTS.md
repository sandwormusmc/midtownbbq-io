# Midtown Smokehouse sites

| Host | Role | Local path |
|------|------|------------|
| https://mts.moldvan.com/ | Marketing site + menu CMS | `mts/` |
| https://mts-order.moldvan.com/ | Ordering SPA prototype | `mts-order/` |

## CMS
- Admin UI: https://mts.moldvan.com/admin/
- Publishes `data/menu.json` via Lambda Function URL (live S3 object)
- Password: `mts/.cms-password` (local only)
- **`deploy.sh` does not upload `data/menu.json`** — site deploys must not wipe CMS publishes; re-add items in admin if a deploy ran before that rule existed
- Deploy marketing: `cd mts && ./deploy.sh`
- Deploy ordering: `cd mts-order && ./deploy.sh`
