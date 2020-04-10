#!/usr/bin/env bash

cleanup() {
    exitcode=$?
    printf 'exit code returned: %s\n' "$exitcode"
    printf 'the command executing at the time of the error was: %s\n' "$BASH_COMMAND"
    printf 'command present on line: %d' "${BASH_LINENO[0]}"
    exit $exitcode
}

trap cleanup ERR

help() {
    echo "Usage: test.sh [/path/to/sonar]"
}

base_dir="."
if [ "$#" -ge 2 ]; then
    help
    exit 1
elif [ "$#" == 1 ]; then
    base_dir=$1
fi

rm -rf "$base_dir"/tmp
mkdir "$base_dir"/tmp
# shellcheck source=/dev/null
source "$SONAR_PATH"/shell/sonar.sh

cd "$base_dir"/tmp || return
sonar create repo sample
cd sample || return
sonar repo activate sample
sonar board activate ad_8k5
sonar activate vivado_2017.2
sonar create ip sample

cd "$base_dir" || return
cp sample.cpp tmp/sample/sample/src/
cp sample.hpp tmp/sample/sample/include/
cp sample.py tmp/sample/sample/testbench/

cd tmp/sample || return
