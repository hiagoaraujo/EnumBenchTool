#!/bin/sh 
echo ">> Creating .tar folder..."
version="0.11.4"
tar -cvzf "enum-bench-tool-"$version".tar" "src/" "config/" "setup.sh"
mv "enum-bench-tool-"$version".tar" $HOME
echo ">> done!"
