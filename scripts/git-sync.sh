#!/usr/bin/env bash
# git-sync.sh - safely sync the current feature branch with origin/<base>, check, push,
# and optionally promote <base> to the feature branch (fast-forward only).
#
# Usage:
#   scripts/git-sync.sh [--dry-run] [--check "CMD"] [--to-main [--yes]] [--base BRANCH]
#
#   --dry-run     fetch and show the plan; change nothing (no merge, push, checkout)
#   --check CMD   run CMD (e.g. "pytest -q") on the merged state; push only if it passes
#   --to-main     after the push, fast-forward BASE to the branch and push BASE (asks first)
#   --yes         skip the confirmation prompt for --to-main (needed without a terminal)
#   --base B      base branch (default: main)
#
# Guarantees:
#   - refuses on a dirty tree, detached HEAD, or the base branch itself
#   - refuses if origin/<branch> has commits you do not have (pull first)
#   - fast-forwards when possible; otherwise checks conflicts with merge-tree BEFORE merging
#   - aborts a failed merge (git merge --abort); never leaves the repo mid-merge
#   - never pushes if --check fails
#   - --to-main only fast-forwards; never creates a merge commit on the base
# Requires: git >= 2.38 (merge-tree --write-tree).

set -u

BASE="main"; DRY=0; CHECK=""; TO_MAIN=0; YES=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --check)   CHECK="${2:-}"; shift ;;
    --to-main) TO_MAIN=1 ;;
    --yes)     YES=1 ;;
    --base)    BASE="${2:-}"; shift ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

say()  { echo "[git-sync] $*"; }
fail() { echo "STOP: $*" >&2; exit 1; }
act()  { if [ "$DRY" -eq 1 ]; then echo "  [dry-run] $*"; return 0; fi; "$@"; }

# 0. git version guard
ver=$(git version | awk '{print $3}')
major=$(echo "$ver" | cut -d. -f1); minor=$(echo "$ver" | cut -d. -f2)
if [ "$major" -lt 2 ] || { [ "$major" -eq 2 ] && [ "$minor" -lt 38 ]; }; then
  fail "git $ver is older than 2.38 (merge-tree --write-tree unavailable)"
fi

# 1. branch guards
branch=$(git branch --show-current)
[ -n "$branch" ] || fail "detached HEAD; check out a feature branch"
[ "$branch" != "$BASE" ] || fail "current branch is '$BASE'; switch to a feature branch"

# 2. clean tree (commit or stash first; this script never commits)
if [ -n "$(git status --porcelain)" ]; then
  git status --short
  fail "working tree is not clean; commit (and run your checks) first"
fi

# 3. fetch (read-only for the working tree, allowed in dry-run)
git fetch origin --prune || fail "git fetch failed (network or auth)"

# 4. remote feature branch must not have commits we lack
if git rev-parse -q --verify "origin/$branch" >/dev/null; then
  read -r _ rb < <(git rev-list --left-right --count "HEAD...origin/$branch")
  [ "$rb" -eq 0 ] || fail "origin/$branch has $rb commit(s) not in $branch. Run: git pull --ff-only (or resolve divergence) first"
else
  say "origin/$branch does not exist yet; push will create it"
fi

# 5. base divergence
[ -n "$(git rev-parse -q --verify "origin/$BASE")" ] || fail "origin/$BASE not found"
read -r ahead behind < <(git rev-list --left-right --count "HEAD...origin/$BASE")
say "branch=$branch base=origin/$BASE ahead=$ahead behind=$behind dry_run=$DRY"

pre=$(git rev-parse HEAD)
merged=0

# 6. bring base into the branch
if [ "$behind" -gt 0 ]; then
  if git merge-base --is-ancestor HEAD "origin/$BASE"; then
    say "fast-forward to origin/$BASE (no merge commit)"
    act git merge --ff-only "origin/$BASE" || fail "fast-forward failed"
  else
    tmp=$(mktemp)
    if ! git merge-tree --write-tree --name-only HEAD "origin/$BASE" >"$tmp" 2>&1; then
      echo "Conflicting paths (nothing merged):" >&2
      tail -n +2 "$tmp" >&2
      rm -f "$tmp"
      fail "merge of origin/$BASE would conflict; resolve manually, then re-run"
    fi
    rm -f "$tmp"
    say "conflict check clean; merging origin/$BASE"
    act git merge --no-edit "origin/$BASE" || { git merge --abort 2>/dev/null; fail "merge failed and was aborted; repo unchanged"; }
  fi
  merged=1
else
  say "nothing to merge: origin/$BASE is contained in $branch"
fi

# 7. check the merged state before anything leaves the machine
if [ -n "$CHECK" ]; then
  say "running check: $CHECK"
  if [ "$DRY" -eq 0 ]; then
    if ! bash -c "$CHECK"; then
      if [ "$merged" -eq 1 ]; then fail "check failed; nothing pushed. Local merge is kept; undo with: git reset --keep $pre"; fi
      fail "check failed; nothing pushed"
    fi
  else
    echo "  [dry-run] $CHECK"
  fi
fi

# 8. push the branch
act git push -u origin "$branch" || fail "push failed (remote may have moved; re-run)"

# 9. optional promotion of base (fast-forward only)
if [ "$TO_MAIN" -eq 1 ]; then
  git merge-base --is-ancestor "origin/$BASE" "$branch" || fail "origin/$BASE has commits not in $branch"
  if [ "$(git rev-parse "$BASE")" != "$(git rev-parse "origin/$BASE")" ]; then
    fail "local $BASE differs from origin/$BASE; run: git checkout $BASE && git pull --ff-only"
  fi
  git merge-base --is-ancestor "$BASE" "$branch" || fail "local $BASE is not an ancestor of $branch; refuse to promote"
  if [ "$YES" -eq 0 ]; then
    if [ "$DRY" -eq 1 ]; then
      say "would ask before promoting $BASE to $branch"
    else
      ans=""
      { read -r -p "Fast-forward $BASE to $branch and push $BASE? [y/N] " ans < /dev/tty; } 2>/dev/null \
        || fail "confirmation needed but no terminal; re-run with --yes"
      [ "$ans" = "y" ] || fail "promotion cancelled"
    fi
  fi
  act git checkout "$BASE" || fail "checkout $BASE failed"
  act git merge --ff-only "$branch" || { act git checkout "$branch"; fail "ff-only promotion failed; back on $branch"; }
  act git push origin "$BASE" || { act git checkout "$branch"; fail "push $BASE failed; back on $branch (local $BASE is ahead of origin)"; }
  act git checkout "$branch" || fail "could not return to $branch"
  if [ "$DRY" -eq 1 ]; then say "would promote $BASE to $branch and push $BASE (dry-run)"; else say "promoted $BASE to $branch and pushed $BASE"; fi
fi

if [ "$DRY" -eq 1 ]; then say "dry-run complete: nothing changed"; elif [ "$merged" -eq 1 ]; then say "done: $branch pushed (merged origin/$BASE)"
else say "done: $branch pushed (no merge needed)"; fi
