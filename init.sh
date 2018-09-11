#!/bin/bash

if [[ $# !=  2 ]]; then
    echo "Usage: init.sh /abs/path/to/repository /abs/path/to/vivado_hls/include"
    return 0
fi

repoPath=$1
vivadoPath=$2
configFile=~/.sonar

if [[ -f $configFile ]]; then
  echo "Initialization already run!"
  return 0
fi

touch $configFile
echo "#!/bin/bash" >> $configFile

mkdir -p $repoPath/sample/build
mkdir -p $repoPath/sample/build/bin
mkdir -p $repoPath/sample/build/vivado_hls
mkdir -p $repoPath/sample/build/vivado

sudo apt-get install python-yaml

echo "" >> $configFile
echo "#--- Begin: added by SONAR ---#" >> $configFile

echo "export SONAR_PATH=$repoPath" >> $configFile
echo "export SONAR_VIVADO_HLS=$vivadoPath" >> $configFile

echo "" >> $configFile

echo 'if [[ -z "$PYTHONPATH" ]]; then' >> $configFile
echo '  export PYTHONPATH=$SONAR_PATH' >> $configFile
echo "else" >> $configFile
echo '  for x in $SONAR_PATH; do' >> $configFile
echo '    case ":$PYTHONPATH:" in' >> $configFile
echo '      *":$x:"*) :;; # already there' >> $configFile
echo '      *) PYTHONPATH="$x:$PYTHONPATH";;' >> $configFile
echo "    esac" >> $configFile
echo "  done" >> $configFile
echo "fi" >> $configFile
echo "#--- End: added by SONAR ---#" >> $configFile
echo "" >> $configFile

echo "" >> ~/.bashrc
echo "source $configFile #added by sonar" >> ~/.bashrc
source ~/.bashrc