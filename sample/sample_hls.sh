#!/bin/bash

old_path=$PWD
file="sample"
mkdir -p $SONAR_PATH/sample/build
mkdir -p $SONAR_PATH/sample/build/bin
mkdir -p $SONAR_PATH/sample/build/vivado_hls
mkdir -p $SONAR_PATH/sample/build/vivado
vivado_hls_dir=$SONAR_PATH/sample/build/vivado_hls

cd $vivado_hls_dir
vivado_hls -f $SONAR_PATH/sample/${file}_hls.tcl
cd $old_path