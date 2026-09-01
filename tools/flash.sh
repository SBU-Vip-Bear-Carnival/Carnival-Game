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

if [ ! -e "$SERIAL_PORT" ]; then
  echo "No board at $SERIAL_PORT" >&2
  echo "Connected boards:" >&2
  arduino-cli board list >&2
  echo >&2
  echo "Fix SERIAL_PORT in tools/.env" >&2
  exit 1
fi

echo "Compiling..."
arduino-cli compile --profile mega firmware/carnival
echo "Uploading to $SERIAL_PORT..."
arduino-cli upload --profile mega -p "$SERIAL_PORT" firmware/carnival
echo "Done."
