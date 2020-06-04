#!/usr/bin/env bash

help_message="
run.sh MODE [args]

cad
    project mode sim create synth impl bit export
        project: name of the project
        mode: batch | gui | tcl
        sim: 0 | behav
        create: 0 | 1
        synth: 0 | 1
        impl: 0 | 1
        bit: 0 | 1
        export: 0 | 1
"

basePath=BASE_PATH

if [[ "$#" == 0 || $1 == '--h' || $1 == '-help' ]]; then
    echo -e "$help_message"
    exit 1
fi

if [[ $1 == 'cad' && "$#" == 9 ]]; then
    make -C $basePath sim-"$2" VIV_MODE="$3" VIV_SIM="$4" VIV_CREATE="$5" VIV_SYNTH="$6" VIV_IMPL="$7" VIV_BIT="$8" VIV_EXPORT="$9"
else
    echo -e "$help_message"
    exit 1
fi
