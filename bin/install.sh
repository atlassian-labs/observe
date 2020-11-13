#!/usr/bin/env bash

if [[ ! -d .ve ]]; then
  python -m venv .ve --prompt="(observe)"
fi

pip install --upgrade pip
pip install -r requirements.txt
