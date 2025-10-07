#!/bin/bash

set -eu
cd "$(dirname ${BASH_SOURCE[0]})"

. .venv/bin/activate

tmpfile=$(mktemp)
trap 'rm -f -- "$tmpfile"' INT TERM HUP EXIT

{
    printf '# List of moregvm tools\n\n'
    printf 'A list of all tools with their --help output follows:\n'
    for tool in src/moregvm/tools/*.py ; do
        tool=${tool##*/}
        tool=${tool%.py}
        printf '\n## %s\n```\n' "$tool"
        printf 'generating %s help...\n' "$tool" 1>&2
        $tool --help
        printf '```\n'
    done
} > "$tmpfile"

mv -v -T -- "$tmpfile" ./TOOLS.md
