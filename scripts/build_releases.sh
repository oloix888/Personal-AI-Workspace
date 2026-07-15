#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
OUT="$ROOT/build/releases"
rm -rf "$ROOT/build"
mkdir -p "$OUT"
cat "$ROOT"/source/creator/part-*.md > "$OUT/Personal-AI-Workspace-Creator-v1.5.1.md"
current="$OUT/Personal-AI-Workspace-Creator-v1.5.1.md"
reverse_step() {
  local previous="$1" patch_file="$2"
  local output="$OUT/Personal-AI-Workspace-Creator-v${previous}.md"
  patch --silent --reverse --output="$output" "$current" < "$ROOT/$patch_file"
  current="$output"
}
reverse_step 1.5 history/patches/v1.5-to-v1.5.1.patch
reverse_step 1.4 history/patches/v1.4-to-v1.5.patch
reverse_step 1.3 history/patches/v1.3-to-v1.4.patch
reverse_step 1.2 history/patches/v1.2-to-v1.3.patch
reverse_step 1.1 history/patches/v1.1-to-v1.2.patch
reverse_step 1.0 history/patches/v1.0-to-v1.1.patch
(cd "$OUT" && sha256sum *.md > SHA256SUMS.txt)
echo "Built $(find "$OUT" -name '*.md' | wc -l | tr -d ' ') release files"
