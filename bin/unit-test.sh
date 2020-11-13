
#!/usr/bin/env bash

set -ex

cd "$(dirname "${BASH_SOURCE[0]}")/.."
# For module imports
. .ve/bin/activate
export PYTHONPATH="${PYTHONPATH}:`pwd`/observe"
export NO_JSON_LOGGING=1
export NO_CHECK_REQUIRED_VARS=1

if [ -z "$1" ]; then
    path="test/unit_tests/"
else
    path="$1"
fi

if ! pytest --cov=observe -v -s $path; then
    fail=$(($fail + 1))
fi

exit $fail
