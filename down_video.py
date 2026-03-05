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


def transcode_and_replace(src: Path, ff_loc: str | None):
    if ff_loc:
        ffmpeg_bin = str(Path(ff_loc) / 'ffmpeg.exe')
    else:
        ffmpeg_bin = 'ffmpeg'

    dst = src.with_name(src.stem + '_h264.mp4')
    cmd = [
        ffmpeg_bin, '-y', '-i', str(src),
        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-movflags', '+faststart',
        str(dst)
    ]
    rc = subprocess.run(cmd).returncode
    if rc != 0:
        print('Gagal convert H.264')
        sys.exit(rc)

    try:
        src.unlink(missing_ok=True)
    except Exception:
        pass

    # rename hasil akhir jadi nama asli (biar 1 file final saja)
    final = src.with_suffix('.mp4')
    try:
        if final.exists():
            final.unlink()
    except Exception:
        pass
    dst.rename(final)
    print(f'Selesai: {final}')


def main():
    url = input('Masukkan URL video (FB/IG/YT): ').strip()
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
        '-f', 'bestvideo[fps>=60]+bestaudio/bestvideo+bestaudio/best',
        '--merge-output-format', 'mp4',
        '-o', tpl,
    ]
    if ff_loc:
        cmd += ['--ffmpeg-location', ff_loc]
    cmd += [url]

    before = set(DEFAULT_OUT.glob('*.mp4'))
    rc = subprocess.run(cmd).returncode
    if rc != 0:
        sys.exit(rc)

    after = set(DEFAULT_OUT.glob('*.mp4'))
    new_files = sorted(list(after - before), key=lambda p: p.stat().st_mtime)
    if not new_files:
        print('Download selesai, tapi file mp4 tidak ditemukan.')
        return

    newest = new_files[-1]
    transcode_and_replace(newest, ff_loc)


if __name__ == '__main__':
    main()
