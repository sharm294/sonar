#!/usr/bin/env bash

# This shell script initializes Sonar. It sets up the SONAR_PATH and
# SONAR_VIVADO_HLS environment variables. It also adds Sonar to the
# PYTHONPATH environment variable so python scripts can be run from anywhere.

configFile=~/.sonar

if [[ -f $configFile ]]; then
  echo "Sonar initialization already run! Source 'purge.sh' to delete"
  return 0
fi

echo "************************"
echo "* sonar initialization *"
echo "************************"
echo ""

echo "Enter the absolute path to this repository:"
echo "It should end in '.../sonar' (remove trailing /)"
echo "[used for making internal file references]"
read -er repoPath
echo ""

echo "Enter the absolute path to the Vivado HLS include folder:"
echo "Leave blank to skip setting this env variable"
echo "[used to enable the Vivado HLS based sample project]"
read -er vivadoPath

touch $configFile
echo "#!/usr/bin/env bash" >> $configFile

echo "export SONAR_PATH=$repoPath" >> $configFile
if [[ $vivadoPath != "" ]]; then
  echo "export SONAR_VIVADO_HLS=$vivadoPath" >> $configFile
fi

{
  echo "" >> $configFile

  # add sonar to the PYTHONPATH environment variable if it's not already there.
  echo 'if [[ -z "$PYTHONPATH" ]]; then'
  echo '  export PYTHONPATH=$SONAR_PATH'
  echo "else"
  echo '  for x in $SONAR_PATH; do'
  echo '    case ":$PYTHONPATH:" in'
  echo '      *":$x:"*) :;; # already there'
  echo '      *) PYTHONPATH="$x:$PYTHONPATH";;'
  echo "    esac"
  echo "  done"
  echo "fi"
} >> $configFile

echo "" >> ~/.bashrc
echo "source $configFile # added by sonar" >> ~/.bashrc
source ~/.bashrc

mkdir -p $SONAR_PATH/sample
mkdir -p $SONAR_PATH/sample/build
mkdir -p $SONAR_PATH/sample/build/bin
