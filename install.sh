#!/bin/bash
#To avoid permission issue: chmod +x install.sh
#1. Install SARead
cd ./SARead
mkdir tmp
cd ./tmp/
cmake ..
make
mv SARead ../
cd ../
rm -rf ./tmp
#2. Install SADisplay
cd ../SADisplay
mkdir tmp
cd ./tmp/
cmake ..
make
mv SADisplay ../
cd ../
rm -rf ./tmp
