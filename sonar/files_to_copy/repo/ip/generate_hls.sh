#!/usr/bin/env bash

if [[ "$#" != 1 ]]; then
    echo "Syntax: script moduleName"
    exit 1
fi

old_path=$PWD
basePath=BASE_PATH
file=$1

hlsDir=$basePath/hls
projectPath=$hlsDir/projects/$SONAR_HLS_VERSION
solutionPath=$projectPath/$file/$SONAR_PART_FAMILY
ipPath=$solutionPath/impl/ip
repoPath=$hlsDir/repo/$SONAR_CAD_VERSION/$SONAR_PART_FAMILY/$file

prefixedName=${file}_${file}
finalName=$file

mkdir -p "$projectPath"
mkdir -p "$repoPath"
cd "$projectPath" || exit
vivado_hls -f $hlsDir/generate_hls.tcl "$file"
vivado_return=$?
if [[ $vivado_return != 0 ]]; then
    exit $vivado_return
fi
cat "$solutionPath"/syn/report/"${finalName}"_csynth.rpt
mkdir -p "$repoPath"
rm -rf "${repoPath:?}"/*
sed -i "s/\b$prefixedName\b/${file}/g" "$ipPath"/run_ippack.tcl
sed -i "s/set DisplayName \"${file^}_${finalName}\"/set DisplayName \"${finalName}\"/g" \
    "$ipPath"/run_ippack.tcl
sed -i "s/\b$prefixedName\b/${finalName}/g" \
    "$ipPath"/hdl/vhdl/"${prefixedName}".vhd
sed -i "s/\b$prefixedName\b/${finalName}/g" \
    "$ipPath"/hdl/verilog/"${prefixedName}".v
sed -i "s/\b$prefixedName\b/${finalName}/g" \
    "$ipPath"/bd/bd.tcl
mv "$ipPath"/hdl/vhdl/"${prefixedName}".vhd \
    "$ipPath"/hdl/vhdl/"${finalName}".vhd
mv "$ipPath"/hdl/verilog/"${prefixedName}".v \
    "$ipPath"/hdl/verilog/"${finalName}".v
cd "$ipPath" || exit
./pack.sh
zipFile=xilinx_com_hls_${file}_1_0.zip
cp "$ipPath"/"$zipFile" "$repoPath"
cd "$repoPath" || exit
unzip -o "$zipFile" -d .
rm "$zipFile"
cd "$old_path" || exit

# call IP specific script if it exists
if [[ -f "$hlsDir/$file.sh" ]]; then
    # shellcheck source=/dev/null
    source "$hlsDir/$file.sh"
fi
