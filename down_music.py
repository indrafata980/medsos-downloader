#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

DEFAULT_OUT = Path('downloads')
DEFAULT_FFMPEG = Path(r'D:\download\ffmpeg-2026-03-01-git-862338fe31-full_build\bin')


def platform_tag(url: str) -> str:
    host = (urlparse(url).netloc or '').lower()
    if 'youtube.com' in host or 'youtu.be' in host:
        return 'YT'
    if 'instagram.com' in host:
        return 'IG'
    if 'facebook.com' in host or 'fb.watch' in host:
        return 'FB'
    return 'WEB'


def ffmpeg_location() -> str | None:
    return str(DEFAULT_FFMPEG) if DEFAULT_FFMPEG.exists() else None


def main():
    url = input('Masukkan URL audio (FB/IG/YT): ').strip()
    if not url:
        print('URL kosong.')
        return

    DEFAULT_OUT.mkdir(parents=True, exist_ok=True)
    date = datetime.now().strftime('%Y%m%d')
    tag = platform_tag(url)
    tpl = str(DEFAULT_OUT / f'{date}_{tag}_%(id)s.%(ext)s')

    ff_loc = ffmpeg_location()
    cmd = [
        sys.executable, '-m', 'yt_dlp',
        '--no-playlist', '--newline',
        '--js-runtimes', 'deno,node,bun,quickjs',
        '-f', 'bestaudio/best',
        '--extract-audio', '--audio-format', 'mp3',
        '-o', tpl,
    ]
    if ff_loc:
        cmd += ['--ffmpeg-location', ff_loc]
    cmd += [url]

    rc = subprocess.run(cmd).returncode
    if rc != 0:
        sys.exit(rc)

    print(f'Selesai. Cek folder: {DEFAULT_OUT.resolve()}')


if __name__ == '__main__':
    main()
