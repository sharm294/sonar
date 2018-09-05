#!/bin/bash

repoPath=$1
vivadoPath=$2
configFile = ~/.shoal

if [[ -f ${repoPath}/.initialized ]]; then
  echo "Initialization already run!"
  exit
fi

touch ${repoPath}/.initialized

echo "" >> configFile
echo "#--- Begin: added by SHOAL-SHARE ---#" >> configFile

if [[ -z "${SHOAL_SHARE_PATH}" ]]; then
  echo "export SHOAL_SHARE_PATH=$repoPath" >> configFile
fi

if [[ -z "${SHOAL_VIVADO_HLS_INC}" ]]; then
  echo "export SHOAL_VIVADO_HLS_INC=$vivadoPath" >> configFile
fi
echo "" >> configFile

echo 'if [[ -z "$PYTHONPATH" ]]; then' >> configFile
echo '  export PYTHONPATH=$SHOAL_SHARE_PATH' >> configFile
echo "else" >> configFile
echo '  for x in $SHOAL_SHARE_PATH; do' >> configFile
echo '    case ":$PYTHONPATH:" in' >> configFile
echo '      *":$x:"*) :;; # already there' >> configFile
echo '      *) PYTHONPATH="$x:$PYTHONPATH";;' >> configFile
echo "    esac" >> configFile
echo "  done" >> configFile
echo "fi" >> configFile
echo "#--- End: added by SHOAL-SHARE ---#" >> configFile
echo "" >> configFile

echo "source $configFile #added by shoal-share" >> ~/.bashrc
source ~/.bashrc
