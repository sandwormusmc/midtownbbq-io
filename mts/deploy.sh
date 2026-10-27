#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
[[ -f "$ROOT/.deploy.env" ]] && source "$ROOT/.deploy.env"
export AWS_PROFILE="${AWS_PROFILE:-moldvan.com-admin}"
BUCKET="${BUCKET:-midtownbbq-io}"
DIST_ID="${DIST_ID:?DIST_ID required}"

# Avoid uploading local secrets / tooling / broken symlinks
aws s3 sync "$ROOT/" "s3://$BUCKET/" \
  --exclude "deploy.sh" --exclude "*.md" --exclude ".DS_Store" \
  --exclude ".deploy.env" --exclude ".cms-password" --exclude "cms-api/*" \
  --exclude "pages/brand-kit" --exclude "pages/brand-kit/**" \
  --exclude "data/menu.json" \
  --exclude ".git/*" --exclude ".gitignore" \
  --delete

aws s3 cp "$ROOT/index.html" "s3://$BUCKET/index.html" \
  --cache-control "public,max-age=60" --content-type "text/html; charset=utf-8"

aws s3 sync "$ROOT/pages/" "s3://$BUCKET/pages/" \
  --exclude "brand-kit" --exclude "brand-kit/**" --exclude "*.md" \
  --cache-control "public,max-age=60"

aws s3 sync "$ROOT/brand-kit/" "s3://$BUCKET/brand-kit/" \
  --cache-control "public,max-age=86400"

# data/menu.json is owned by the CMS (admin publish) — never overwrite from git/local seed on deploy

aws s3 sync "$ROOT/admin/" "s3://$BUCKET/admin/" \
  --cache-control "public,max-age=60"

aws cloudfront create-invalidation --distribution-id "$DIST_ID" --paths "/*" >/dev/null
echo "Deployed https://mts.moldvan.com/ (invalidated $DIST_ID)"
echo "Admin: https://mts.moldvan.com/admin/"
echo "Order: https://mts-order.moldvan.com/"
