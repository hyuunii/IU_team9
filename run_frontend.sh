#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR/frontend"

if [ ! -x node_modules/.bin/vinext ]; then
  npm install
fi

exec npm run dev
