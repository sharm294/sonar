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
# create a repo named 'ethernet_repo' in the current directory
sonar create repo ethernet_repo
cd ethernet_repo || return

# activate vivado 2017.2, use this repo,
# set the board to an Alpha Data 8k5
sonar activate vivado_2017.2
sonar repo activate ethernet_repo
sonar board activate ad_8k5

# create an IP in this directory named 'ethernet_ip'
sonar create ip ethernet_ip

cd "$base_dir" || return
# add user-developed src files and a testbench
cp ethernet.v tmp/ethernet_repo/ethernet_ip/src/
cp ethernet.py tmp/ethernet_repo/ethernet_ip/testbench/

cd tmp/ethernet_repo/ethernet_ip || return

# update the generated Makefile to add the source file
sed -i 's/hdl_modules =/hdl_modules = ethernet/g' sonar.mk

# generate the sonar TB
make config-ethernet

# create a vivado project for ethernet and simulate it in terminal
./run.sh cad ethernet batch behav 1 0 0 0 0 > vivado.log
