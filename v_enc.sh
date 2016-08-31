#!/bin/bash

filelist=(
http://source/video1.mp4
http://source/video2.mp4
http://source/video3.mp4
http://source/video4.mp4
)

for i in "${filelist[@]}"; do
  name=${i##*/}
  decoded=$(printf '%b' "${name//%/\\x}")
  bname=${decoded%.*}
  avconv -i "$i" -codec copy "$bname.flv"

  #timestamp=$( date +%s%3N )
  #avconv -i "$i" -codec copy "out_$timestamp.flv"
done
