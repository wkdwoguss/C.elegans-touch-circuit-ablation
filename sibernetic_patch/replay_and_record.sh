#!/bin/bash
# Replays an already-completed Sibernetic simulation (position_buffer.txt etc. already
# on disk) and records the screen to mp4 -- skips the c302/physics computation entirely.
# Mirrors the "Step 3" replay+record portion of master_openworm.py.
set -e

SIM_DIR="$1"   # e.g. /home/ow/sibernetic/simulations/C2_TouchTW_AVDablated_2026-07-14_02-09-51
CONFIG="${2:-worm_crawl_half_resolution}"

cd "$SIBERNETIC_HOME"
DISPLAY_NUM=:44
export DISPLAY=$DISPLAY_NUM

echo "Starting Xvfb..."
Xvfb $DISPLAY_NUM -listen tcp -ac -screen 0 1920x1080x24+32 &
sleep 3
xhost + || true

mkdir -p "$OW_OUT_DIR/output"
SIM_NAME=$(basename "$SIM_DIR")
NEW_OUT="$OW_OUT_DIR/output/$SIM_NAME"
mkdir -p "$NEW_OUT"
MOVIE="$SIM_NAME.mp4"

echo "Starting tmux recording session..."
tmux new-session -d -P -s SiberneticRecording \
  "DISPLAY=$DISPLAY_NUM ffmpeg -r 30 -f x11grab -draw_mouse 0 -s 1920x1080 -i $DISPLAY_NUM -filter:v crop=1200:800:100:100 -cpu-used 0 -b:v 384k -qmin 10 -qmax 42 -maxrate 384k -bufsize 1000k -an $NEW_OUT/$MOVIE"
sleep 3
tmux list-sessions

echo "Replaying simulation from $SIM_DIR ..."
./Release/Sibernetic -f "$CONFIG" -l_from lpath="$SIM_DIR"
echo "Replay finished."

tmux send-keys -t SiberneticRecording q
tmux send-keys -t SiberneticRecording "exit" C-m
sleep 3
tmux list-sessions || true

ls -la "$NEW_OUT"

echo "Trimming leading black frames..."
OUTSTR=$(ffmpeg -i "$NEW_OUT/$MOVIE" -vf blackdetect=d=0:pic_th=0.70:pix_th=0.10 -an -f null - 2>&1 | grep blackdetect | head -1 || true)
echo "blackdetect: $OUTSTR"
BLACK_START=0.0
BLACK_DUR=""
if [ -n "$OUTSTR" ]; then
  BLACK_START=$(echo "$OUTSTR" | sed -n 's/.*black_start:\([0-9.]*\).*/\1/p')
  BLACK_DUR=$(echo "$OUTSTR" | sed -n 's/.*black_duration:\([0-9.]*\).*/\1/p')
fi
if [ "$BLACK_START" = "0.0" ] && [ -n "$BLACK_DUR" ]; then
  BD=$(python3 -c "import math; print(int(math.ceil(float('$BLACK_DUR'))))")
  if [ "$BD" -gt 9 ]; then
    ffmpeg -ss "00:00:$BD" -i "$NEW_OUT/$MOVIE" -c copy -avoid_negative_ts 1 "$NEW_OUT/cut_$MOVIE"
  else
    ffmpeg -ss "00:00:0$BD" -i "$NEW_OUT/$MOVIE" -c copy -avoid_negative_ts 1 "$NEW_OUT/cut_$MOVIE"
  fi
fi

echo "Speeding up..."
mkdir -p /tmp/speedup_tmp
SRC_FOR_SPEEDUP="$NEW_OUT/$MOVIE"
[ -f "$NEW_OUT/cut_$MOVIE" ] && SRC_FOR_SPEEDUP="$NEW_OUT/cut_$MOVIE"
ffmpeg -ss 1 -i "$SRC_FOR_SPEEDUP" -vf "select=gt(scene\,0.1)" -vsync vfr -vf fps=fps=1/1 /tmp/speedup_tmp/out%06d.jpg
ffmpeg -r 100 -i /tmp/speedup_tmp/out%06d.jpg -r 100 -vb 60M "$NEW_OUT/speeded_$MOVIE"
rm -rf /tmp/speedup_tmp

echo "DONE. Files in $NEW_OUT:"
ls -la "$NEW_OUT"
