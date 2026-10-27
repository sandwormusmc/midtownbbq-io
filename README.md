# moldvan.com workspace

Agent instructions: [AGENTS.md](AGENTS.md). Shell alias: `mm`.

Local workspace for the WordPress site and Midtown Smokehouse. No git repo.

| Area | What |
|------|------|
| WordPress | https://www.moldvan.com — REST API, details in `docs/WORDPRESS.md` |
| `mts/` | https://mts.moldvan.com/ marketing site and menu CMS |
| `mts-order/` | https://mts-order.moldvan.com/ ordering SPA |
| `mts/handout/` | Print and TV menu handout |

WordPress edits use the application password in `~/.wp-app-password`. Midtown static deploys use `AWS_PROFILE=moldvan.com-admin` and `./deploy.sh` in the site directory.
