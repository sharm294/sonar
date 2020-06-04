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
sonar create repo sample_repo
cd sample_repo || return
sonar activate vivado_2017.2
sonar repo activate sample_repo
sonar board activate ad_8k5
sonar create ip sample_ip

cd "$base_dir" || return
cp sample_src.cpp tmp/sample_repo/sample_ip/src/
cp sample_src.hpp tmp/sample_repo/sample_ip/include/
cp sample_src.py tmp/sample_repo/sample_ip/testbench/

cd tmp/sample_repo/sample_ip || return

sed -i 's/c_modules =/c_modules = sample_src/g' sonar.mk
make hw-sample_src
make config-sample_src
./run.sh cad sample_src batch behav 1 0 0 0 0
