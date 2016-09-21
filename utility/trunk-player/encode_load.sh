#!/bin/sh
# Wrapper script to import new audio files into trunk-player
# * Encode the wav files into mp3
# * If the wav is from an analog TG increase the volume to match the digital groups
# * Upload the new mp3 to amazon s3
#
# Dylan Reinhold dreinhold@gmail.com
#--------------------------------------------------------------------------

BASE_DIR="/home/myuser"
LOG="$BASE_DIR/audio/encode.log"

S3_BUCKET="scanoc-audio-001"

# Load python virtual environment
. $BASE_DIR/trunk-player/env/bin/activate

basename="$1"
filename="$basename.wav"
mp3encoded="$basename.mp3"
json="$basename.json"

echo "$basename : `date` encode $basename" >> $LOG

grep '"analog": 0' $BASE_DIR/audio/$json >/dev/null 2>&1
if [ $? -eq 0 ]
then
    echo "$basename : `date` digital" >> $LOG
    lame --preset voice "$BASE_DIR/audio/$filename" "$BASE_DIR/audio/$mp3encoded" >> $LOG
else
    echo "$basename : `date` analog" >> $LOG
    lame --scale 7 --preset voice "$BASE_DIR/audio/$filename" "$BASE_DIR/audio/$mp3encoded" >> $LOG
fi

$BASE_DIR/trunk-player/utility/trunk-player/upload_to_s3_delete.py $BASE_DIR/audio/$mp3encoded $S3_BUCKET >> $LOG 2>&1
$BASE_DIR/trunk_player/utility/trunk-player/load_audio_file.sh $basename

rm -f $BASE_DIR/audio/$filename
