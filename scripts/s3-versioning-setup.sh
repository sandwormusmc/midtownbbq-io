#!/usr/bin/env bash
set -euo pipefail

# -------------------------------------------------------------------------
# 1️⃣  Enable versioning on the bucket that stores the hand‑out static site
# -------------------------------------------------------------------------
BUCKET="midtownbbq-io"

echo "🔧 Enabling versioning on bucket: $BUCKET"
aws s3api put-bucket-versioning \
  --bucket "$BUCKET" \
  --versioning-configuration Status=Enabled

# -------------------------------------------------------------------------
# 2️⃣  Apply a lifecycle rule that keeps only the 5 most recent
#     non‑current versions of each object.
# -------------------------------------------------------------------------
cat > /tmp/lifecycle.json <<'EOF'
{
  "Rules": [
    {
      "ID": "keep-5-noncurrent",
      "Status": "Enabled",
      "Filter": {},
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 30,
        "NewerNoncurrentVersions": 5
      }
    }
  ]
}
EOF

echo "📦 Adding lifecycle rule (keep 5 non‑current versions, expire after 30 days)"
aws s3api put-bucket-lifecycle-configuration \
  --bucket "$BUCKET" \
  --lifecycle-configuration file:///tmp/lifecycle.json

echo "✅ S3 versioning & lifecycle configuration complete."
