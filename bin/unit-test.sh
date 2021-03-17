#!/usr/bin/env bash

if [[ ! -d .ve ]]; then
  python -m venv .ve --prompt="(observe)"
fi

source .ve/bin/activate

export PYTHONPATH="${PYTHONPATH}:`pwd`/observe"

if [ -z "$1" ]; then
    path="test/unit/"
else
    path="$1"
fi

if ! pytest --cov=atl_observe --cov-report=xml -v -s $path; then
    fail=$(($fail + 1))
fi

exit $fail
