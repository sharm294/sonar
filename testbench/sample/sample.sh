#!/bin/bash

old_path=$PWD
file="sample"
vivado_hls_dir=$SHOAL_SHARE_PATH/testbench/sample/build/vivado_hls

cd $vivado_hls_dir
vivado_hls -f $SHOAL_SHARE_PATH/testbench/sample/$file.tcl
cd $old_path