#!/usr/bin/env bash

# For module imports
. .ve/bin/activate

echo "flake8... "
if ! flake8 "./observe" "./test"; then
    fail=$(($fail + 1))
fi
echo "Result: ${fail}"

echo "pylint..."
if ! pylint -E `find ./observe ./test -name '*.py'`; then
    fail=$(($fail + 1))
fi
echo "Result: ${fail}"

echo "isort..."
if ! isort -c `find ./observe ./test -name '*.py'`; then
    fail=$(($fail + 1))
fi
echo "Result: ${fail}"

exit $fail
