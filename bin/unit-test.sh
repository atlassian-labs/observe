#!/usr/bin/env bash
export PYTHONPATH="${PYTHONPATH}:`pwd`/observe"

if [ -z "$1" ]; then
    path="test/unit_tests/"
else
    path="$1"
fi

if ! pytest --cov=observe -v -s $path; then
    fail=$(($fail + 1))
fi

exit $fail
