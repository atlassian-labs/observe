#!/usr/bin/env bash

set -e

[[ "$0" = "$BASH_SOURCE" ]] && set -x

if [[ ! -d .ve ]]; then
  python -m venv .ve --prompt="(observe)"
fi

pip install --upgrade pip
pip install -r requirements.txt
