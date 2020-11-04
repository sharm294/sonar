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
# create a repo named 'hello_world_repo' in the current directory
sonar create repo hello_world_repo
cd hello_world_repo || return

# activate vivado 2017.2, use this repo,
# set the board to an Alpha Data 8k5
sonar activate vivado_2017.2
sonar repo activate hello_world_repo
sonar board activate ad_8k5

# create an IP in this directory named 'hello_world_ip'
sonar create ip hello_world_ip

cd "$base_dir" || return
# add user-developed src files and a testbench
cp hello_world.cpp tmp/hello_world_repo/hello_world_ip/src/
cp hello_world.hpp tmp/hello_world_repo/hello_world_ip/include/
cp hello_world.py tmp/hello_world_repo/hello_world_ip/testbench/

cd tmp/hello_world_repo/hello_world_ip || return

# update the generated Makefile to add the source file
sed -i 's/c_modules =/c_modules = hello_world/g' sonar.mk

# generate the HLS IP
make hw-hello_world

# generate the sonar TB
make config-hello_world

# run the C++ TB
make cpptb-hello_world
make runtb-hello_world

# create a vivado project for hello_world and simulate it in terminal
./run.sh cad hello_world batch behav 1 0 0 0 0
