#!/bin/bash

old_path=$PWD
file="sample"
vivado_hls_dir=$SHOAL_SHARE_PATH/sample/build/vivado_hls

mkdir -p vivado_hls_dir
mkdir -p $vivado_hls_dir/projects
cd $vivado_hls_dir/projects
vivado_hls -f $SHOAL_SHARE_PATH/sample/$file.tcl
cd $old_path
