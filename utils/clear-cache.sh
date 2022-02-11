#!/bin/sh
ROOT="$(dirname "$0")"
find "$ROOT/../auto_flutter" -iname "__pycache__" -type d | xargs -d '\n' rm -r