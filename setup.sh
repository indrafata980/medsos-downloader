#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")"

echo "[1/3] Update packages..."
pkg update -y

echo "[2/3] Install dependencies (python, ffmpeg, pip)..."
pkg install -y python ffmpeg python-pip

echo "[3/3] Install Python requirements..."
pip install -r requirements.txt

echo "Setup done."
echo "Run:"
echo "  python down_video.py"
echo "  python down_music.py"
echo "  python downcli_menu.py"
