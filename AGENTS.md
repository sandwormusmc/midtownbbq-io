# Agent guide — moldvan.com

OpenCode loads this file. Shell alias: `mm`.

Workspace for [moldvan.com](https://www.moldvan.com) and the Midtown Smokehouse sites. There is no git repo. WordPress changes go through the REST API. Static Midtown sites deploy to S3.

## WordPress (moldvan.com)

- Site: `https://www.moldvan.com` (also `https://moldvan.com`).
- Credentials: application password in `~/.wp-app-password` (user `matt`, strip spaces). Use WP REST `wp/v2` with Basic Auth.
- Edit content through the API. Change files on the server only for media ownership, Apache config, plugins, or debugging.
- Document root on the server: `/var/www/matthewmoldvan.com/httpsdocs/wordpress`.
- vhost: `ServerName www.moldvan.com`, `ServerAlias moldvan.com`.
- Detail: `docs/WORDPRESS.md`.

## Midtown Smokehouse

| Tree | Live | Notes |
|------|------|--------|
| `mts/` | https://mts.moldvan.com/ | Marketing site + menu CMS. Deploy: `AWS_PROFILE=moldvan.com-admin ./deploy.sh` from that directory |
| `mts-order/` | https://mts-order.moldvan.com/ | Ordering SPA. Same deploy pattern. `/api` is proxied to kitchen-new |
| `mts/handout/` | local print/TV handout | Built from `menu.json`; see that folder's README |

CMS admin password is `.cms-password` inside `mts/` (local only). `mts/deploy.sh` does not upload `data/menu.json`; menu publishes stay on the CMS path. Read `mts/README.md`, `mts-order/README.md`, and `docs/MTS.md` before deploying.

## Other skills

- MakerWorld print posts on the WordPress blog: `~/.cursor/skills/makerworld-print-workflow/SKILL.md`
- Calendar links: `~/.cursor/skills/google-calendar/SKILL.md`

Do not commit or paste the WordPress application password or the CMS password.

## Domain Registration: midtownbbq.io

- **Registered in**: Route 53 (account `699560170742`)
- **Hosted Zone ID**: `Z093275977P83FS0G13`
- **CloudFront Distribution**: `E293E6RVQ0BLMD`
- **SSL Certificate**: `arn:aws:acm:us-east-1:699560170742:certificate/f19dfe45-9d7f-49f5-ace3-fd354df8b83e`

**Certificate SANs** (Subject Alternative Names):
- `moldvan.com` (original domain)
- `*.moldvan.com` (wildcard)
- `*.midtownbbq.io` (wildcard)

**DNS Records** (all in Route 53 hosted zone `Z093275977P83FS0G13`):

| Record Name | Type | Target | Purpose |
|-------------|------|--------|---------|
| `midtownbbq.io.` | A (Alias) | `d3m6ggmwpgystp.cloudfront.net.` | Root domain → CloudFront |
| `www.midtownbbq.io.` | CNAME | `d3m6ggmwpgystp.cloudfront.net` | WWW → CloudFront |
| `_b2d35a51870ac15e9f28597c72a0f4c0.midtownbbq.io.` | CNAME | `_e3d2016d60d74fd7cbf8b871b0dd2208.wzccmgtwzk.acm-validations.aws.` | ACM validation for *.midtownbbq.io |
| `*.midtownbbq.io.` | CNAME (via ACM) | ACM validation domain | Wildcard certificate validation |

**Redirect Behavior**:
- All traffic to `midtownbbq.io`, `www.midtownbbq.io`, or `*.midtownbbq.io` goes to CloudFront distribution `E293E6RVQ0BLMD`
- CloudFront serves content from `mts.moldvan.com.s3.us-east-1.amazonaws.com` (S3 bucket with static website hosting)
- S3 bucket redirect configured to send all requests to `https://mts.moldvan.com/`

**Commands for verification**:
```bash
# Check domain registration
aws --profile moldvan.com-admin route53domains list-domains | grep midtownbbq

# Check hosted zone
aws --profile moldvan.com-admin route53 list-hosted-zones | grep midtownbbq

# Check CloudFront distribution
aws --profile moldvan.com-admin cloudfront get-distribution --id E293E6RVQ0BLMD

# Check DNS resolution
dig +short midtownbbq.io
dig +short www.midtownbbq.io

# Check certificate SANs
aws --profile moldvan.com-admin acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:699560170742:certificate/f19dfe45-9d7f-49f5-ace3-fd354df8b83e \
  | jq '.Certificate.SubjectAlternativeNames'
```
