#!/bin/bash

old_path=$PWD
file="sample"
vivado_hls_dir=$SONAR_PATH/sample/build/vivado_hls

cd $vivado_hls_dir
vivado_hls -f $SONAR_PATH/sample/${file}_hls.tcl
cd $old_path