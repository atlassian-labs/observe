#!/usr/bin/env bash

set -e

if [[ ! -d .ve ]]; then
  python3 -m venv .ve --prompt="(observe)"
fi

source .ve/bin/activate

pip install --upgrade pip
pip install wheel
pip install twine

python3 setup.py sdist bdist_wheel

twine check dist/*