#!/usr/bin/env bash

if [[ ! -d .ve ]]; then
  python -m venv .ve --prompt="(observe)"
fi

source .ve/bin/activate

if ! flake8 "./observe" "./test"; then
    fail=$(($fail + 1))
fi

if ! pylint -E `find ./observe ./test -name '*.py'`; then
    fail=$(($fail + 1))
fi

if ! isort -c `find ./observe ./test -name '*.py'`; then
    fail=$(($fail + 1))
fi

exit $fail
