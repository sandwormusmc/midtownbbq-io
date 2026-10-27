#!/usr/bin/env bash
set -euo pipefail

# -------------------------------------------------------------------------
# 2️⃣  Initialise a git repository in the workspace root
# -------------------------------------------------------------------------
cd "$(dirname "$(realpath "$0")")/.."   # go to project root (~/projects/moldvan.com)

if [ -d ".git" ]; then
  echo "⚠️  A git repo already exists – nothing to do."
  exit 0
fi

echo "🗂️  Initialising git repository"
git init

# Basic .gitignore – ignore temporary files, AWS credentials, etc.
cat > .gitignore <<'EOF'
# OS / editor artefacts
.DS_Store
Thumbs.db
*.log
node_modules/
tmp/
*.tmp
*.swp

# AWS / cloud‑cli artefacts
.aws/
*.pem

# Sensitive local files (do NOT commit)
~/.wp-app-password
mts/.cms-password
EOF

git add .

git commit -m "Initial commit – handout HTML + stylesheet, MkDocs, deployment scripts"

echo "✅ Git repo created and initial commit recorded."
echo "You can now add a remote (e.g. GitHub) with:"
echo "   git remote add origin <YOUR‑REPO‑URL>"
echo "   git push -u origin master"
