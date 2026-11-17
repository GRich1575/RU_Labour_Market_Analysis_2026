#!/usr/bin/env bash
# Sync current feature branch with origin/main, then push.
# Usage: scripts/git-sync.sh [base-branch]   (default base: main)
# Requires: clean working tree, git >= 2.38 (merge-tree --write-tree).
# Refuses to run on the base branch itself (pushing main needs explicit confirmation).

set -u
BASE="${1:-main}"

fail() { echo "STOP: $*" >&2; exit 1; }

# 0. Version guard
ver=$(git version | awk '{print $3}')
major=$(echo "$ver" | cut -d. -f1); minor=$(echo "$ver" | cut -d. -f2)
if [ "$major" -lt 2 ] || { [ "$major" -eq 2 ] && [ "$minor" -lt 38 ]; }; then
  fail "git $ver is older than 2.38 (merge-tree --write-tree unavailable)"
fi

branch=$(git branch --show-current)
[ -n "$branch" ] || fail "detached HEAD"
[ "$branch" != "$BASE" ] || fail "current branch is '$BASE'; switch to a feature branch"

# 1. Clean tree
if [ -n "$(git status --porcelain)" ]; then
  git status --short
  fail "working tree is not clean; commit or stash first"
fi

# 2. Fetch
git fetch origin || fail "git fetch failed"

# 3. Divergence: ahead = commits only in branch, behind = commits only in origin/BASE
read -r ahead behind < <(git rev-list --left-right --count "HEAD...origin/$BASE" | awk '{print $1, $2}')
echo "branch=$branch ahead=$ahead behind=$behind (vs origin/$BASE)"

merged=0
if [ "$behind" -gt 0 ]; then
  # 4. Conflict check without touching the working tree
  if ! git merge-tree --write-tree --name-only HEAD "origin/$BASE" > /tmp/mt.out 2>&1; then
    echo "Conflicting paths:" >&2
    tail -n +2 /tmp/mt.out >&2
    fail "merge of origin/$BASE would conflict; resolve manually"
  fi
  # 5. Merge
  git merge --no-edit "origin/$BASE" || fail "merge failed"
  merged=1
else
  echo "Nothing to merge: origin/$BASE is already contained in $branch."
fi

# 6. Push only if there is something new to send
if [ "$ahead" -eq 0 ] && [ "$merged" -eq 0 ]; then
  echo "Nothing to push: $branch has no new commits and nothing was merged."
  exit 0
fi
git push origin "$branch" || fail "push failed"
echo "Pushed $branch."
