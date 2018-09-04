#!/bin/bash

repoPath=$1
vivadoPath=$2

if [[ -f ${repoPath}/.initialized ]]; then
  echo "Initialization already run!"
  exit
fi

touch ${repoPath}/.initialized

GASCORE_PATH=${GIT_PATH}/GASCore
SHARE_PATH=${GIT_PATH}/share

echo "" >> ~/.bashrc
echo "#--- Begin: added by SHOAL-SHARE ---#" >> ~/.bashrc

if [[ -z "${SHOAL_SHARE_PATH}" ]]; then
  echo "export SHOAL_SHARE_PATH=$repoPath" >> ~/.bashrc
fi

if [[ -z "${SHOAL_VIVADO_HLS_INC}" ]]; then
  echo "export SHOAL_VIVADO_HLS_INC=$vivadoPath" >> ~/.bashrc
fi
echo "" >> ~/.bashrc

echo 'if [[ -z "$PYTHONPATH" ]]; then' >> ~/.bashrc
echo '  export PYTHONPATH=$SHOAL_SHARE_PATH' >> ~/.bashrc
echo "else" >> ~/.bashrc
echo '  for x in $SHOAL_SHARE_PATH; do' >> ~/.bashrc
echo '    case ":$PYTHONPATH:" in' >> ~/.bashrc
echo '      *":$x:"*) :;; # already there' >> ~/.bashrc
echo '      *) PYTHONPATH="$x:$PYTHONPATH";;' >> ~/.bashrc
echo "    esac" >> ~/.bashrc
echo "  done" >> ~/.bashrc
echo "fi" >> ~/.bashrc
echo "#--- End: added by SHOAL-SHARE ---#" >> ~/.bashrc
echo "" >> ~/.bashrc

source ~/.bashrc
