#!/bin/bash

set -eu
cd "$(dirname ${BASH_SOURCE[0]})"

if [[ -e .venv ]] ; then
    printf 'Error: .venv already exists. delete it if you want to redo setup\n' 1>&2
    exit 1
fi

printf '+ python3 -m venv --system-site-packages .venv\n'
python3 -m venv --system-site-packages .venv

printf '+ . .venv/bin/activate\n'
. .venv/bin/activate

printf '+ python3 -m pip install --no-build-isolation --editable .\n'
python3 -m pip install --no-build-isolation --editable .
