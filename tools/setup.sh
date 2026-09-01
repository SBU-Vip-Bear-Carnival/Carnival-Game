#!/usr/bin/env bash
# One-time setup. Safe to re-run.
set -euo pipefail

cd "$(dirname "$0")/.."
echo "Carnival Game — setup"
echo

# --- 1. arduino-cli -----------------------------------------------------
if ! command -v arduino-cli >/dev/null 2>&1; then
  echo "  arduino-cli is not installed."
  echo "    macOS:  brew install arduino-cli"
  echo "    other:  https://arduino.github.io/arduino-cli/latest/installation/"
  echo
  echo "  Install it, then run this script again."
  exit 1
fi
echo "  ok   arduino-cli $(arduino-cli version | awk '{print $3}')"

# --- 2. pre-push hook: refuse to push main ------------------------------
if [ ! -d .git/hooks ]; then
  echo "  WARN no .git/hooks/ -- this is not a git clone, skipping the pre-push hook."
  echo "       Clone the repo properly if you intend to push."
  HOOK=/dev/null
else
  HOOK=.git/hooks/pre-push
  # Re-running is safe, but someone else's hook is not ours to throw away.
  if [ -f "$HOOK" ] && ! grep -q 'refs/heads/main' "$HOOK" 2>/dev/null; then
    cp "$HOOK" "$HOOK.bak.$(date +%Y%m%d%H%M%S)"
    echo "  ..   backed up your existing pre-push hook"
  fi
fi
cat > "$HOOK" <<'HOOKEOF'
#!/usr/bin/env bash
# Refuses a direct push to main. Work on a branch and open a pull request --
# see docs/GIT-WORKFLOW.md.
while read -r _local_ref _local_sha remote_ref _remote_sha; do
  if [ "$remote_ref" = "refs/heads/main" ]; then
    echo
    echo "  BLOCKED: you are pushing straight to main."
    echo
    echo "  Put this on a branch instead:"
    echo "      git checkout -b feat/my-change"
    echo "      git push -u origin feat/my-change"
    echo
    echo "  Then open a pull request. See docs/GIT-WORKFLOW.md"
    echo
    exit 1
  fi
done
exit 0
HOOKEOF
if [ "$HOOK" != /dev/null ]; then
  chmod +x "$HOOK"
  echo "  ok   pre-push hook installed (blocks pushes to main)"
fi

# --- 3. host-side env ---------------------------------------------------
if [ -f tools/.env ]; then
  echo "  ok   tools/.env already present"
elif [ -f tools/.env.example ]; then
  cp tools/.env.example tools/.env
  echo "  ok   created tools/.env — set your serial port in it"
else
  echo "  WARN tools/.env.example is missing; create tools/.env by hand before flashing"
fi

# --- 4. prove the toolchain works ---------------------------------------
echo
echo "  Compiling firmware to verify the toolchain (first run downloads ~40MB)..."
if arduino-cli compile --profile mega firmware/carnival >/dev/null 2>&1; then
  echo "  ok   firmware compiles"
else
  echo "  FAIL firmware did not compile. Run this to see why:"
  echo "         arduino-cli compile --profile mega firmware/carnival"
  exit 1
fi

echo
echo "Done. Read docs/GIT-WORKFLOW.md before you write any code."
