#!/usr/bin/env bash

if [[ ! -d .ve ]]; then
  python -m venv .ve --prompt="(observe)"
fi

source .ve/bin/activate

if ! flake8 "./atl_observe" "./test"; then
    fail=$(($fail + 1))
fi

if ! pylint -E `find ./atl_observe ./test -name '*.py'`; then
    fail=$(($fail + 1))
fi

if ! isort -c `find ./atl_observe ./test -name '*.py'`; then
    fail=$(($fail + 1))
fi

exit $fail
