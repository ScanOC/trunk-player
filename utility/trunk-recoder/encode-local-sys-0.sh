#! /bin/bash
# Sample file for loading local files into trunk-player
# Dylan Reinhold 03/10/2017
# Project https://github.com/ScanOC/trunk-player
#-------------------------------------------------------
echo "Encoding: $1" 
filename="$1"
basename="${filename%.*}"
filename_only=$(basename $basename)
mp3encoded="$basename.mp3"
json="$basename.json"
web_dir=$(dirname $filename | cut -d/ -f6-)"/"
system=0 # Change this for each system

# Hack the JSON to add play length and source
len=$(soxi -D $filename)

head -n-2 $json > $json.new
echo "\"play_length\": $len," >> $json.new
echo "\"source\": 0," >> $json.new
tail -n2 $json >> $json.new
mv $json.new $json

lame --preset voice $filename $mp3encoded

cd /home/radio/trunk-player
. env/bin/activate
./manage.py add_transmission $basename --web_url=$web_dir --system=$system
rm -f $filename $json

