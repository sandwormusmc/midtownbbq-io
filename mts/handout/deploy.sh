#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# Load shared deploy env from parent mts directory
source "$ROOT/../.deploy.env"
export AWS_PROFILE="${AWS_PROFILE:-moldvan.com-admin}"
BUCKET="${BUCKET:-midtownbbq-io}"
DIST_ID="${DIST_ID:?DIST_ID required}"

# Sync handout files, excluding internal resources
aws s3 sync "$ROOT/" "s3://$BUCKET/handout/" \
  --exclude "deploy.sh" --exclude "*.md" --exclude "*.py" --exclude "__pycache__/*" \
  --exclude "assets/generated/*" --delete \
  --cache-control "public,max-age=60"

# Invalidate CloudFront cache for updated handout files
aws cloudfront create-invalidation --distribution-id "$DIST_ID" --paths "/handout/*"

echo "Deployed handout to https://midtownbbq.io/handout/"