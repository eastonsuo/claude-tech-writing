#!/usr/bin/env bash
# 把 tech-writing/ 打包成 ZIP，供上传到 Claude.ai
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
rm -f tech-writing.zip
zip -rq tech-writing.zip tech-writing/ -x "*.DS_Store" -x "*__pycache__*"
echo "✓ Built tech-writing.zip ($(ls -lh tech-writing.zip | awk '{print $5}'))"
echo "  Upload via Claude.ai: + button → Skills → Add skill → 选这个 ZIP"
