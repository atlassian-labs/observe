#!/usr/bin/env sh

set -e

if [[ ! -d .ve ]]; then
  python -m venv .ve --prompt="(observe)"
fi

pip install --upgrade pip
pip install -r requirements.txt
