#!/bin/bash

# This shell script initializes Sonar. It sets up the SONAR_PATH and 
# SONAR_VIVADO_HLS environment variables. It creates directories that are 
# assumed to exist by the other scripts in Sonar. It also adds Sonar to the 
# PYTHONPATH environment variable so python scripts can be run from anywhere.

if [[ $# !=  1 && $# != 2 ]]; then
    echo "Usage: init.sh /abs/path/to/repository [/abs/path/to/vivado_hls/include]"
    return 0
fi

repoPath=$1
if [[ $# == 2 ]]; then
  vivadoPath=$2
fi
configFile=~/.sonar

if [[ -f $configFile ]]; then
  echo "Sonar initialization already run!"
  return 0
fi

touch $configFile
echo "#!/bin/bash" >> $configFile

mkdir -p $repoPath/sample/build
mkdir -p $repoPath/sample/build/bin
mkdir -p $repoPath/sample/build/vivado_hls
mkdir -p $repoPath/sample/build/vivado

echo "" >> $configFile
echo "#--- Begin: added by SONAR ---#" >> $configFile

echo "export SONAR_PATH=$repoPath" >> $configFile
if [[ $# == 2 ]]; then
  echo "export SONAR_VIVADO_HLS=$vivadoPath" >> $configFile
fi

echo "" >> $configFile

# add sonar to the PYTHONPATH environment variable if it's not already there.
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