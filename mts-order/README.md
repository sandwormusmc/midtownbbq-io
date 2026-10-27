# Midtown Smokehouse — ordering SPA

**Live:** https://mts-order.moldvan.com/

Swipeable mobile ordering (Home → Menu → Detail → Cart → Checkout → Confirm).  
Checkout posts to same-origin `/api` (CloudFront → kitchen-new → Midtown staging API).

Marketing site: https://mts.moldvan.com/

## Infra
- S3: `mts-order.moldvan.com` (SPA)
- CloudFront: `EY6PVG51087Q8` — default → S3; `/api*` + `/health*` → `mts-order-origin.moldvan.com`
- Origin host: kitchen-new Apache → `127.0.0.1:3010` (`midtown-staging.service`)
- ACM: `*.moldvan.com` (us-east-1)
- Route53: `mts-order.moldvan.com` → CloudFront; `mts-order-origin.moldvan.com` A → kitchen-new (origin only)

## Deploy
```bash
export AWS_PROFILE=moldvan.com-admin
./deploy.sh
```
