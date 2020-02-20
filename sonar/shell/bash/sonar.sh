#!/usr/bin/env bash

# This bash function overrides the 'sonar' executable when this script is sourced.
sonar() {
    # call the actual sonar Python executable
    command sonar $@

    # if the command was an 'activate', source the profile script to update
    if [[ $# -ge 2 ]]; then
        if [[ $1 == "activate" ]]; then
            # source ~/.sonar/shell/bash/sourceme.sh
            echo "Sourced file"
        fi
    fi
}
