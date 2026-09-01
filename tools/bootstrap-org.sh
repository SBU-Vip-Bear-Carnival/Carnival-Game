#!/usr/bin/env bash
#
# One-time org and repo setup. Run once, after the organization exists.
#
#   ./tools/bootstrap-org.sh <org-name>
#
# GitHub has no API for creating an organization on github.com, so that one step
# is manual: https://github.com/account/organizations/new  (pick the Free plan).
# Everything after it is here, in code, so the permission config is a file
# someone can read rather than a set of clicks nobody wrote down.
#
# Safe to re-run: each step is idempotent or skips if already done.
#
set -euo pipefail

ORG="${1:-}"
REPO="Carnival-Game"

if [ -z "$ORG" ]; then
  echo "usage: $0 <org-name>" >&2
  exit 1
fi

command -v gh >/dev/null || { echo "gh CLI not installed" >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "run: gh auth login" >&2; exit 1; }

# Creating teams and changing org settings needs admin:org. A default gh login
# does not have it, and the failure without this check is an opaque 403.
SCOPES=$(gh auth status 2>&1 | grep -o 'Token scopes:.*' || true)
if [ -z "$SCOPES" ] || echo "$SCOPES" | grep -qi 'none'; then
  # A fine-grained PAT or GH_TOKEN auth reports no OAuth scopes even when it can
  # do everything here. Do not reject it -- let the first real call be the judge.
  echo "==> note: cannot read OAuth scopes (fine-grained PAT or token auth)."
  echo "    Continuing. If a call returns 403, the token lacks org admin rights."
elif ! echo "$SCOPES" | grep -q 'admin:org'; then
  echo "Your gh token is missing the 'admin:org' scope." >&2
  echo "Grant it, then re-run:" >&2
  echo "    gh auth refresh -h github.com -s admin:org" >&2
  exit 1
fi

if ! gh api "orgs/$ORG" >/dev/null 2>&1; then
  echo "Organization '$ORG' does not exist, or you cannot see it." >&2
  echo "Create it first: https://github.com/account/organizations/new" >&2
  exit 1
fi
echo "==> org $ORG found"

# 2FA cannot be set through the API -- it is read-only there -- so this checks
# rather than configures. It is a hard stop on purpose: turning 2FA on AFTER
# people join silently removes everyone who has not enabled it, which reads to
# them as GitHub breaking rather than as a policy.
TWOFA=$(gh api "orgs/$ORG" --jq '.two_factor_requirement_enabled' 2>/dev/null || echo null)
case "$TWOFA" in
  true)
    echo "==> 2FA required: yes"
    ;;
  false)
    echo >&2
    echo "  STOP: two-factor authentication is not required for this org." >&2
    echo >&2
    echo "  Turn it on BEFORE inviting anyone:" >&2
    echo "    https://github.com/organizations/$ORG/settings/security" >&2
    echo "    -> Require two-factor authentication" >&2
    echo >&2
    echo "  Then re-run this script." >&2
    exit 1
    ;;
  *)
    # GitHub returns this field only to org owners; absent is not the same as off.
    echo "==> WARN: cannot read the 2FA setting -- you are probably not an owner"
    echo "    of $ORG. Confirm with an owner that 2FA is required before inviting"
    echo "    anyone. Continuing; the next call will fail if you lack admin."
    ;;
esac

# --- 1. Org-wide defaults ----------------------------------------------
# Base permission Read: members can see every repo, but nobody can push
# directly to one. Push access comes only from team membership.
echo "==> org defaults: base permission = read, repo creation = owners only"
gh api -X PATCH "orgs/$ORG" \
  -f default_repository_permission=read \
  -F members_can_create_repositories=false \
  -F members_can_create_public_repositories=false \
  -F members_can_fork_private_repositories=false \
  --silent

# --- 2. The repo -------------------------------------------------------
if gh api "repos/$ORG/$REPO" >/dev/null 2>&1; then
  echo "==> repo $ORG/$REPO already exists, skipping creation"
else
  echo "==> creating private repo $ORG/$REPO"
  gh repo create "$ORG/$REPO" --private \
    --description "Accessible carnival game for United Cerebral Palsy of Long Island. Arduino Mega firmware and hardware, built by Stony Brook VIP BEAR." \
    >/dev/null
fi

# --- 3. Repo settings (these work on any plan) -------------------------
# Squash-only keeps main linear and forgives messy WIP commits inside a PR.
# Auto-delete stops the branch graveyard V1 accumulated.
echo "==> repo settings: squash-only, auto-delete branches"
gh api -X PATCH "repos/$ORG/$REPO" \
  -F allow_squash_merge=true \
  -F allow_merge_commit=false \
  -F allow_rebase_merge=false \
  -F delete_branch_on_merge=true \
  -F allow_update_branch=true \
  -F has_wiki=false \
  --silent

# --- 4. Teams ----------------------------------------------------------
# Created empty on purpose. Write = push a branch and open a PR; it does NOT
# mean merge to main. That combination is what "everyone works on their own
# branch" is, mechanically.
for team in electronics software mechanical; do
  if gh api "orgs/$ORG/teams/$team" >/dev/null 2>&1; then
    echo "==> team $team exists"
  else
    echo "==> creating team $team"
    gh api -X POST "orgs/$ORG/teams" \
      -f name="$team" \
      -f description="VIP BEAR $team subteam" \
      -f privacy=closed --silent
  fi
  # A freshly created team's slug can take a moment to resolve; without this
  # the PUT 404s and set -e aborts after the repo already exists.
  for attempt in 1 2 3 4 5; do
    if gh api -X PUT "orgs/$ORG/teams/$team/repos/$ORG/$REPO" \
         -f permission=push --silent 2>/dev/null; then
      break
    fi
    if [ "$attempt" = 5 ]; then
      echo "    FAILED to grant $team write on $REPO after 5 tries" >&2
      exit 1
    fi
    sleep 2
  done
  echo "    granted write on $REPO"
done

# --- 5. Branch ruleset on main -----------------------------------------
# NOTE: on a free org this SAVES but does not ENFORCE for a private repo --
# rulesets need GitHub Team. A faculty educator who owns the org can enable
# Team for free from the GitHub Education dashboard. Until then the pre-push
# hook in tools/setup.sh and a visible red CI check are what carry this.
if gh api "repos/$ORG/$REPO/rulesets" --jq '.[].name' 2>/dev/null | grep -qx "main"; then
  echo "==> ruleset 'main' already exists, skipping"
else
  echo "==> creating ruleset on main"
  gh api -X POST "repos/$ORG/$REPO/rulesets" --input - --silent <<'JSON'
{
  "name": "main",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "bypass_actors": [],
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": true
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [ { "context": "build" } ]
      }
    }
  ]
}
JSON
fi

# --- 6. Report ---------------------------------------------------------
echo
echo "=============================================================="
gh api "repos/$ORG/$REPO" --jq '"repo:        \(.full_name) (\(.visibility))"'
gh api "repos/$ORG/$REPO" --jq '"merge:       squash=\(.allow_squash_merge) merge=\(.allow_merge_commit) rebase=\(.allow_rebase_merge)"'
gh api "repos/$ORG/$REPO" --jq '"autodelete:  \(.delete_branch_on_merge)"'
gh api "orgs/$ORG" --jq '"base perm:   \(.default_repository_permission)"'
echo "teams:       $(gh api "orgs/$ORG/teams" --jq '[.[].slug] | join(", ")')"
echo "rulesets:    $(gh api "repos/$ORG/$REPO/rulesets" --jq '[.[].name] | join(", ")')"
echo "=============================================================="
echo
echo "Still to do by hand:"
echo "  1. Invite M. Ete Chan and Richard McKenna as org OWNERS."
echo "     You cannot change your own role -- a second owner is the only way"
echo "     you ever get removed when you graduate."
echo "  2. Ask one of them to verify as a GitHub educator and upgrade the org"
echo "     to Team (free): https://github.com/settings/education/benefits"
echo "     Until that lands the ruleset above is saved but NOT enforced, and"
echo "     main stays force-pushable by anyone with write."
echo "  3. Invite the current roster into the teams (2FA is already required,"
echo "     so tell them to enable it before you send the invite)."
