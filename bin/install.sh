#!/usr/bin/env bash

set -e

if [[ ! -d .ve ]]; then
  python -m venv .ve --prompt="(observe)"
fi

source .ve/bin/activate

pip install --upgrade pip
pip install --upgrade pip-tools

pip-sync requirements/requirements.txt
