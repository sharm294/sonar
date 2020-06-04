#!/usr/bin/env bash

help() {
    echo "Usage: vivado_setup /path/to/Xilinx/xilinx_pathectory version"
    echo "       ex. vivado_setup /opt/Xilinx 2018.3"
}

print_versions() {
    xilinx_path=$1
    version=$2

    if [ -d "$xilinx_path/Vivado" ]; then
        echo "Versions available: $(find "$xilinx_path"/Vivado -maxdepth 1 -mindepth 1 -type d -exec basename {} \; | tr "\n" " ")"
    fi
}

if [ -z "$2" ]; then
    help
    return 1
fi

xilinx_path=$(readlink -f "$1")
version=$2

if [ ! -d "$xilinx_path/Vivado" ]; then
    echo "Error: No Vivado installs found at $xilinx_path"
    return 1
fi

if [ ! -d "$xilinx_path/Vivado/$version" ]; then
    echo "Error: Invalid version specified"
    print_versions "$xilinx_path" "$version"
    return 1
fi

# shellcheck disable=SC2034
# set $DIR to hold the current path if needed in the settings.sh scripts
DIR="$xilinx_path"
# shellcheck source=/dev/null
source "$xilinx_path"/DocNav/.settings64-DocNav.sh
# shellcheck source=/dev/null
source "$xilinx_path"/Vivado/"$version"/settings64.sh
