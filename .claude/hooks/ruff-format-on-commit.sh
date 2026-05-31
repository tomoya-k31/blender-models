#!/bin/sh
# PreToolUse/Bash フック: `git commit` を検出したときだけ ruff で整形してから通す。
# Claude Code には commit イベントが無いため、Bash コマンド文字列を検査して判定する。
set -e

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""')

# git commit を含むコマンド以外は何もしない (許可)
case "$cmd" in
*"git commit"*) ;;
*) exit 0 ;;
esac

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# リポジトリ全体を整形 (ruff は .gitignore を尊重)。
# `git add -A && git commit` 形式ではこの後の add で整形結果が取り込まれる。
uv run ruff format . >/dev/null 2>&1 || exit 0

# 既にステージ済みの .py があれば整形後の内容で再ステージ (bare `git commit` 対応)。
staged=$(git diff --cached --name-only --diff-filter=ACMR -- '*.py')
[ -n "$staged" ] && printf '%s\n' "$staged" | xargs git add

exit 0
