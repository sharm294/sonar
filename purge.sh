#!/usr/bin/env bash

# This script purges Sonar from the environment and bashrc. The repo can then 
# be deleted without any other trace

make clean
rm -rf ~/.sonar
rm -rf $SONAR_PATH/sample/build
sed -i '/added by sonar/d' ~/.bashrc
unset SONAR_PATH
unset SONAR_VIVADO_HLS
source ~/.bashrc