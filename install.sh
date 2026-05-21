#!/usr/bin/env bash
# install.sh — symlink the tech-writing skill into ~/.claude/skills/

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="tech-writing"
SKILLS_DIR="$HOME/.claude/skills"
SOURCE="$REPO_DIR/$SKILL_NAME"
TARGET="$SKILLS_DIR/$SKILL_NAME"

if [ ! -d "$SOURCE" ]; then
  echo "✗ Skill source not found at $SOURCE" >&2
  exit 1
fi

mkdir -p "$SKILLS_DIR"

if [ -L "$TARGET" ]; then
  existing="$(readlink "$TARGET")"
  if [ "$existing" = "$SOURCE" ]; then
    echo "✓ Already installed (symlink points to $SOURCE)"
    exit 0
  fi
  echo "→ Replacing existing symlink ($existing → $SOURCE)"
  rm "$TARGET"
elif [ -e "$TARGET" ]; then
  echo "✗ $TARGET already exists and is not a symlink." >&2
  echo "  Back it up or remove it manually, then re-run." >&2
  exit 1
fi

ln -s "$SOURCE" "$TARGET"
echo "✓ Linked $SOURCE → $TARGET"
echo
echo "Next steps:"
echo "  1. Restart Claude Code if it's running"
echo "  2. Try: ask 'write a technical article about <X>' — the skill auto-invokes"
echo "  3. Or call it explicitly: /tech-writing"
