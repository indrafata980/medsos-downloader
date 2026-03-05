@echo off
cd /d %~dp0
echo [1/2] Installing Python requirements...
py -m pip install -U pip
py -m pip install -r requirements.txt

echo [2/2] Checking ffmpeg...
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
  echo WARNING: ffmpeg not found in PATH.
  echo Please install ffmpeg or set path in script DEFAULT_FFMPEG.
) else (
  ffmpeg -version | findstr /C:"ffmpeg version"
)

echo.
echo Setup done.
 echo Run:
 echo   py down_video.py
 echo   py down_music.py
 echo   py downcli_menu.py
pause
