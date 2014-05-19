#!/bin/sh 
echo ">> Creating root folder..."
root_folder="/enum-bench-tool"
rm -rf $HOME$root_folder
mkdir $HOME$root_folder
echo ">> done!"

echo ">> Copying source files..."
cp -r "src/" $HOME$root_folder"/src"
cp -r "config/" $HOME$root_folder"/config"
echo ">> done!"

echo ">> Creating auxliar folders..."
mkdir $HOME$root_folder"/bind"
mkdir $HOME$root_folder"/nsd"
mkdir $HOME$root_folder"/pdns"
mkdir $HOME$root_folder"/temp"
mkdir $HOME$root_folder"/log"
mkdir $HOME$root_folder"/query-files"
echo ">> done!"

echo ">> Creating path.dat file..."
echo "//Paths" > $HOME$root_folder"/config/paths.dat"
echo "BIND_FOLDER_PATH\t"$HOME$root_folder"/bind/" >> $HOME$root_folder"/config/paths.dat"
echo "NSD_FOLDER_PATH\t"$HOME$root_folder"/nsd/" >> $HOME$root_folder"/config/paths.dat"
echo "PDNS_FOLDER_PATH\t"$HOME$root_folder"/pdns/" >> $HOME$root_folder"/config/paths.dat"
echo "BIND_ZONES_FOLDER_PATH\t/etc/bind/" >> $HOME$root_folder"/config/paths.dat"
echo "NSD_ZONES_FOLDER_PATH\t/etc/nsd/" >> $HOME$root_folder"/config/paths.dat"
echo "TEMP_FOLDER_PATH\t"$HOME$root_folder"/temp/" >> $HOME$root_folder"/config/paths.dat"
echo "QUERY_FILES_FOLDER_PATH\t"$HOME$root_folder"/query-files/" >> $HOME$root_folder"/config/paths.dat"
echo "LOG_FOLDER_PATH\t"$HOME$root_folder"/log/" >> $HOME$root_folder"/config/paths.dat"
echo ">> done!"

echo ">> Changing source files mode..."
chmod u+x $HOME$root_folder"/src/enum_bench_tool.py"
echo ">> done!"
echo ">> Setup completed sucessfully!"
