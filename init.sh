#!/bin/bash

if [[ $# !=  3 ]]; then
    echo "Usage: init.sh dependenceMode /abs/path/to/shoal/repository /abs/path/to/vivado_hls/include"
    echo "  dependenceMode: 0 (independent repo) or 1 (submodule of shoal)"
    return 0
fi

mode=$1
repoPath=$2
vivadoPath=$3
configFile=~/.shoal

if [[ $mode == 0 && -f $configFile ]]; then
  echo "Initialization already run!"
  return 0
fi

if [[ $mode == 0 ]]; then
  touch $configFile
  echo "#!/bin/bash" >> $configFile
fi

mkdir -p $repoPath/build
mkdir -p $repoPath/build/bin
mkdir -p $repoPath/testbench/sample/build
mkdir -p $repoPath/testbench/sample/build/bin
mkdir -p $repoPath/testbench/sample/build/vivado_hls
mkdir -p $repoPath/testbench/sample/build/vivado

echo "" >> $configFile
echo "#--- Begin: added by SHOAL-SHARE ---#" >> $configFile

echo "export SHOAL_SHARE_PATH=$repoPath" >> $configFile

if [[ $mode == 0 ]]; then
  echo "export SHOAL_VIVADO_HLS=$vivadoPath" >> $configFile
fi
echo "" >> $configFile

echo 'if [[ -z "$PYTHONPATH" ]]; then' >> $configFile
echo '  export PYTHONPATH=$SHOAL_SHARE_PATH' >> $configFile
echo "else" >> $configFile
echo '  for x in $SHOAL_SHARE_PATH; do' >> $configFile
echo '    case ":$PYTHONPATH:" in' >> $configFile
echo '      *":$x:"*) :;; # already there' >> $configFile
echo '      *) PYTHONPATH="$x:$PYTHONPATH";;' >> $configFile
echo "    esac" >> $configFile
echo "  done" >> $configFile
echo "fi" >> $configFile
echo "#--- End: added by SHOAL-SHARE ---#" >> $configFile
echo "" >> $configFile

if [[ $mode == 0 ]]; then
  echo "" >> ~/.bashrc
  echo "source $configFile #added by shoal" >> ~/.bashrc
  source ~/.bashrc
fi