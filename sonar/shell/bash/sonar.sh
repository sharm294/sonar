#!/usr/bin/env bash

# This bash function overrides the 'sonar' executable when this script is sourced.
sonar() {
    # call the actual sonar Python executable
    command sonar "$@"
    retval=$?

    # if the command was an 'activate', source the profile script to update
    if [[ $retval == 0 && $# -ge 2 ]]; then
        if [[ $1 == "env" && $2 == "activate" ]]; then
            # shellcheck source=/dev/null
            source ~/.sonar/shell/bash/sonar_env.sh
            echo "Sourced file"
        fi
    fi
}
