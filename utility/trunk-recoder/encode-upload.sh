#! /bin/bash
# Script to upload audio from trunk-recorder to 
# web server to be displaied by trunk-player
#
# 02/15/2016 - Dylan Reinhold dreinhold@gmail.com
#-----------------------------------------------------
#
REMOTE_USER_NAME="myuser"
REMOTE_SERVER="127.0.0.1"
REMOTE_AUDIO_FOLDER="/home/$REMOTE_USER_NAME/audio"
REMOTE_IMPORT_SCRIPT="/home/$REMOTE_USER_NAME=/trunk-player/utility/server/encode_load.sh"
echo "Encoding: $1" 
filename="$1"
basename="${filename%.*}"
filename_only=$(basename $basename)
json="$basename.json"

# Hack the JSON to add play length
len=$(soxi -D $filename)

head -n-2 $json > $json.new
echo "\"play_length\": $len," >> $json.new
tail -n2 $json >> $json.new
mv $json.new $json

echo "Upload: $filename" 

scp -q -C ${filename} $json $REMOTE_USER_NAME@$REMOTE_SERVER:$REMOTE_AUDIO_FOLDER/
if [ $? -eq 0 ]
then
  ssh -q $REMOTE_USER_NAME@$REMOTE_SERVER "$REMOTE_IMPORT_SCRIPT $filename_only"
  echo "Remove files"
  rm -f $json $filename 
fi

