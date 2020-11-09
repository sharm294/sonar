#!/usr/bin/env bash

function cleanup() {
    exitcode=$?
    return $exitcode
}

trap cleanup ERR

# shellcheck source=/dev/null
source "$1" "$2"

grep -Fxq "SUCCESS: all tests completed successfully!" vivado.log
