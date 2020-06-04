#!/usr/bin/env bash

_sonar_source_tool(){
    if [[ -f ~/.sonar/shell/sonar_tool.sh ]]; then
        # shellcheck source=/dev/null
        source ~/.sonar/shell/sonar_tool.sh
    fi
}

_sonar_source_board(){
    if [[ -f ~/.sonar/shell/sonar_board.sh ]]; then
        # shellcheck source=/dev/null
        source ~/.sonar/shell/sonar_board.sh
    fi
}

_sonar_source_repo(){
    if [[ -f ~/.sonar/shell/sonar_repo.sh ]]; then
        # shellcheck source=/dev/null
        source ~/.sonar/shell/sonar_repo.sh
    fi
}

# This bash function overrides the 'sonar' executable when this script is sourced.
sonar() {
    # call the actual sonar Python executable
    command sonar "$@"
    retval=$?

    # if the command was an 'activate', source the profile script to update
    if [[ $retval == 0 && $# -ge 2 ]]; then
        if [[ $1 == "env" && $2 == "activate" ]]; then
            _sonar_source_tool
            echo "Sourced file"
        elif [[ $1 == "board" && $2 == "activate" ]]; then
            _sonar_source_board
            echo "Sourced file"
        elif [[ $1 == "repo" && $2 == "activate" ]]; then
            _sonar_source_repo
            echo "Sourced file"
        elif [[ $1 == "activate" ]]; then
            _sonar_source_tool
            _sonar_source_board
            _sonar_source_repo
            echo "Sourced file"
        fi
    fi

    return $retval
}

homedir=$(readlink -f ~)
export SONAR_PATH="$homedir"/.sonar
