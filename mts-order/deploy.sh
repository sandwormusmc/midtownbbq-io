#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
[[ -f "$ROOT/.deploy.env" ]] && source "$ROOT/.deploy.env"
export AWS_PROFILE="${AWS_PROFILE:-moldvan.com-admin}"
BUCKET="${BUCKET:-mts-order.moldvan.com}"
DIST_ID="${DIST_ID:?DIST_ID required}"
aws s3 sync "$ROOT/" "s3://$BUCKET/" \
  --exclude "deploy.sh" --exclude "*.md" --exclude ".DS_Store" --exclude ".deploy.env" \
  --delete
aws s3 cp "$ROOT/index.html" "s3://$BUCKET/index.html" \
  --cache-control "public,max-age=60" \
  --content-type "text/html; charset=utf-8"
aws s3 sync "$ROOT/brand-kit/" "s3://$BUCKET/brand-kit/" \
  --cache-control "public,max-age=86400"
aws cloudfront create-invalidation --distribution-id "$DIST_ID" --paths "/*" >/dev/null
echo "Deployed https://mts-order.moldvan.com/ (invalidated $DIST_ID)"

PAPERCLIP_HOST="${PAPERCLIP_HOST:-matt@192.168.1.205}"
PAPERCLIP_ORDERING="${PAPERCLIP_ORDERING:-~/.paperclip/companies/midtown-smokehouse/design-preview/ordering-spa/}"
DESIGNER_ORDERING="${DESIGNER_ORDERING:-~/.openclaw/workspace-midtown-designer/design-preview/ordering-spa/}"
if [[ "${SKIP_PAPERCLIP_SYNC:-}" != "1" ]]; then
  rsync -az --delete \
    --exclude deploy.sh --exclude .deploy.env --exclude "*.md" --exclude ".DS_Store" \
    "$ROOT/" "$PAPERCLIP_HOST:$PAPERCLIP_ORDERING" || echo "warn: paperclip ordering-spa sync failed"
  rsync -az --delete \
    --exclude deploy.sh --exclude .deploy.env --exclude ".DS_Store" \
    "$ROOT/" "$PAPERCLIP_HOST:$DESIGNER_ORDERING" 2>/dev/null || true
  echo "Synced UI → Paperclip design-preview/ordering-spa/"
fi
