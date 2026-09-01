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
HOOK=.git/hooks/pre-push
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
chmod +x "$HOOK"
echo "  ok   pre-push hook installed (blocks pushes to main)"

# --- 3. host-side env ---------------------------------------------------
if [ ! -f tools/.env ] && [ -f tools/.env.example ]; then
  cp tools/.env.example tools/.env
  echo "  ok   created tools/.env — set your serial port in it"
else
  echo "  ok   tools/.env already present"
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
