#!/usr/bin/env bash
# Compile and upload to the connected board.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f tools/.env ]; then
  echo "tools/.env missing — run ./tools/setup.sh first" >&2
  exit 1
fi
# shellcheck disable=SC1091
source tools/.env

# set -u would kill us before the helpful message below if SERIAL_PORT is unset.
SERIAL_PORT="${SERIAL_PORT:-}"
if [ -z "$SERIAL_PORT" ]; then
  echo "SERIAL_PORT is not set in tools/.env" >&2
  arduino-cli board list >&2
  exit 1
fi

# Windows COM ports are not filesystem paths, so -e can never find them.
case "$SERIAL_PORT" in
  COM*|com*) : ;;
  *)
    if [ ! -e "$SERIAL_PORT" ]; then
      echo "No board at $SERIAL_PORT" >&2
      echo "Connected boards:" >&2
      arduino-cli board list >&2
      echo >&2
      echo "Fix SERIAL_PORT in tools/.env" >&2
      exit 1
    fi
    ;;
esac

echo "Compiling..."
arduino-cli compile --profile mega firmware/carnival
echo "Uploading to $SERIAL_PORT..."
arduino-cli upload --profile mega -p "$SERIAL_PORT" firmware/carnival
echo "Done."
