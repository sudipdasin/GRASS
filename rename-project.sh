#!/bin/bash
# rename-project.sh — Renames GitHub repo + local folder + all files
# Usage: bash rename-project.sh
set -e

OLD_NAME="gh-setup"
NEW_NAME="GRASS"
OLD_DESC="Single-file Python GUI that creates, scaffolds, and syncs GitHub repos with zero manual setup"
NEW_DESC="GitHub Repo Auto Setup and Sync"
TOKEN=""
USERNAME=""

# ============================================================
# STEP 0: Get token from config
# ============================================================
CONFIG="$HOME/.config/gh-setup/config.json"
if [ -f "$CONFIG" ]; then
    TOKEN=$(python3 -c "import json; print(json.load(open('$CONFIG')).get('token',''))")
    USERNAME=$(python3 -c "import json; print(json.load(open('$CONFIG')).get('username',''))")
fi

if [ -z "$TOKEN" ]; then
    echo "ERROR: No token found in $CONFIG"
    echo "Run the app, login, then re-run this script."
    exit 1
fi

echo "=== Renaming $OLD_NAME -> $NEW_NAME ==="
echo "User: @$USERNAME"

# ============================================================
# STEP 1: Rename on GitHub (via API)
# ============================================================
echo ""
echo "[1/6] Renaming repo on GitHub..."
RESPONSE=$(curl -s -X POST \
    "https://api.github.com/repos/$USERNAME/$OLD_NAME" \
    -H "Authorization: token $TOKEN" \
    -H "Accept: application/vnd.github+json" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$NEW_NAME\",\"description\":\"$NEW_DESC\"}")

if echo "$RESPONSE" | grep -q '"full_name"'; then
    echo "  OK - renamed to $NEW_NAME"
else
    echo "  WARNING: $RESPONSE"
    echo "  (May already be renamed, continuing...)"
fi

# ============================================================
# STEP 2: Update git remote
# ============================================================
echo ""
echo "[2/6] Updating git remote..."
cd "/media/backup/IMPORTANT/PROJECTS/GitHub Repo Auto Setup & Sync"
git remote set-url origin "https://github.com/$USERNAME/$NEW_NAME.git"
echo "  Remote: $(git remote get-url origin)"

# ============================================================
# STEP 3: Update PROJECT.txt
# ============================================================
echo ""
echo "[3/6] Updating PROJECT.txt..."
if [ -f "PROJECT.txt" ]; then
    sed -i "s/^name: .*/name: $NEW_NAME/" PROJECT.txt
    sed -i "s/^description: .*/description: $NEW_DESC/" PROJECT.txt
    echo "  name: $NEW_NAME"
    echo "  description: $NEW_DESC"
else
    echo "  (no PROJECT.txt found, skipping)"
fi

# ============================================================
# STEP 4: Update README.md
# ============================================================
echo ""
echo "[4/6] Updating README.md..."
if [ -f "README.md" ]; then
    sed -i "s/# $OLD_NAME/# $NEW_NAME/" README.md
    sed -i "s/$OLD_NAME/$NEW_NAME/g" README.md
    echo "  Updated all references"
else
    echo "  (no README.md found, skipping)"
fi

# ============================================================
# STEP 5: Rename local folder
# ============================================================
echo ""
echo "[5/6] Renaming local folder..."
cd "/media/backup/IMPORTANT/PROJECTS"
if [ -d "GitHub Repo Auto Setup & Sync" ]; then
    mv "GitHub Repo Auto Setup & Sync" "$NEW_NAME"
    echo "  Renamed to: $NEW_NAME/"
    cd "$NEW_NAME"
else
    echo "  (folder not found, staying in current dir)"
fi

# ============================================================
# STEP 6: Commit and push
# ============================================================
echo ""
echo "[6/6] Committing and pushing..."
git add -A
git commit -m "rename: $OLD_NAME -> $NEW_NAME" || echo "  (nothing to commit)"
git push
echo "  Pushed."

# ============================================================
# DONE
# ============================================================
echo ""
echo "============================================"
echo "  DONE"
echo "============================================"
echo ""
echo "  GitHub:  github.com/$USERNAME/$NEW_NAME"
echo "  Local:   /media/backup/IMPORTANT/PROJECTS/$NEW_NAME/"
echo "  Remote:  $(git remote get-url origin)"
echo ""
echo "  Old URL (github.com/$USERNAME/$OLD_NAME) auto-redirects to new."
echo ""
echo "  Next time open the app from:"
echo "    python3 /media/backup/IMPORTANT/PROJECTS/$NEW_NAME/gh-setup-v4.py"   
