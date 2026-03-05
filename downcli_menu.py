#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

DEFAULT_FFMPEG = r"D:\download\ffmpeg-2026-03-01-git-862338fe31-full_build\bin"


def run(cmd):
    return subprocess.run(cmd, text=True)


def run_capture(cmd):
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode != 0:
        print(p.stderr or p.stdout)
        sys.exit(p.returncode)
    return p.stdout


def get_info(url, cookies=None):
    cmd = [sys.executable, "-m", "yt_dlp", "-J", "--no-playlist", "--no-warnings", url]
    if cookies:
        cmd[3:3] = ["--cookies", cookies]
    data = run_capture(cmd)
    return json.loads(data)


def has_ffmpeg(ffmpeg_location=None):
    try:
        if ffmpeg_location and Path(ffmpeg_location).exists():
            p = subprocess.run([str(Path(ffmpeg_location) / "ffmpeg.exe"), "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return p.returncode == 0
        p = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return p.returncode == 0
    except FileNotFoundError:
        return False


def platform_tag(url):
    host = (urlparse(url).netloc or "").lower()
    if "youtube.com" in host or "youtu.be" in host:
        return "YT"
    if "instagram.com" in host:
        return "IG"
    if "facebook.com" in host or "fb.watch" in host:
        return "FB"
    return "WEB"


def output_template(url):
    d = datetime.now().strftime("%Y%m%d")
    p = platform_tag(url)
    return f"{d}_{p}_%(id)s.%(ext)s"


def list_top_formats(info, max_items=20):
    fmts = info.get("formats", [])
    vids = [f for f in fmts if f.get("vcodec") != "none"]
    vids.sort(key=lambda f: ((f.get("height") or 0), (f.get("fps") or 0), (f.get("tbr") or 0)), reverse=True)
    print("\nFormat video teratas:")
    print("id | ext | res | fps | note")
    print("-" * 60)
    for f in vids[:max_items]:
        print(f"{f.get('format_id','?'):>4} | {f.get('ext','?'):>3} | {str(f.get('height') or '?')+'p':>5} | {str(f.get('fps') or '?'):>3} | {f.get('format_note','')}")
    print("-" * 60)


def base_cmd(url, out_dir, cookies=None, ffmpeg_location=None):
    cmd = [
        sys.executable, "-m", "yt_dlp", "--no-playlist", "--newline",
        "--js-runtimes", "deno,node,bun,quickjs",
        "-o", str(out_dir / output_template(url)),
    ]
    if cookies:
        cmd += ["--cookies", cookies]
    if ffmpeg_location:
        cmd += ["--ffmpeg-location", ffmpeg_location]
    return cmd


def transcode_to_h264(mp4_path, ffmpeg_location=None):
    src = Path(mp4_path)
    dst = src.with_name(src.stem + "_h264.mp4")

    if ffmpeg_location and Path(ffmpeg_location).exists():
        ffmpeg_bin = str(Path(ffmpeg_location) / "ffmpeg.exe")
    else:
        ffmpeg_bin = "ffmpeg"

    cmd = [
        ffmpeg_bin, "-y", "-i", str(src),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(dst)
    ]
    print(f"[Transcode] {src.name} -> {dst.name}")
    rc = run(cmd).returncode
    if rc == 0:
        print(f"[OK] playable file: {dst}")
        try:
            src.unlink(missing_ok=True)
            print(f"[Hapus] file asli: {src.name}")
        except Exception as e:
            print(f"[Info] gagal hapus file asli: {e}")
    else:
        print(f"[Gagal transcode] {src}")


def download_video(url, out_dir, res, prefer60, cookies=None, ffmpeg_location=None, force_h264=False):
    out_dir.mkdir(parents=True, exist_ok=True)
    if prefer60:
        fmt = (
            f"bestvideo[height<={res}][fps>=60]+bestaudio/"
            f"bestvideo[height<={res}]+bestaudio/"
            f"best[height<={res}]/best"
        )
    else:
        fmt = f"bestvideo[height<={res}]+bestaudio/best[height<={res}]/best"

    before = set(out_dir.glob("*.mp4"))
    cmd = base_cmd(url, out_dir, cookies, ffmpeg_location) + [
        "-f", fmt,
        "--merge-output-format", "mp4",
        url,
    ]
    print(f"\nMulai download video: {url}")
    rc = run(cmd).returncode
    if rc != 0:
        print(f"[Gagal] {url}")
        return

    if force_h264:
        after = set(out_dir.glob("*.mp4"))
        new_files = sorted(list(after - before), key=lambda p: p.stat().st_mtime)
        for f in new_files:
            transcode_to_h264(f, ffmpeg_location)


def download_audio(url, out_dir, cookies=None, ffmpeg_location=None):
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = base_cmd(url, out_dir, cookies, ffmpeg_location) + [
        "-f", "bestaudio/best",
        "--extract-audio", "--audio-format", "mp3",
        url,
    ]
    print(f"\nMulai download audio: {url}")
    rc = run(cmd).returncode
    if rc != 0:
        print(f"[Gagal] {url}")


def get_urls_interactive():
    print("\nInput URL satu-satu. Enter kosong untuk selesai.")
    urls = []
    while True:
        u = input("URL: ").strip()
        if not u:
            break
        urls.append(u)
    return urls


def get_urls_from_file(path):
    p = Path(path)
    if not p.exists():
        print("File URL tidak ditemukan.")
        return []
    return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.strip().startswith("#")]


def main():
    print("=== DownCLI Interaktif (FB/IG/YT) ===")

    ffmpeg_location = DEFAULT_FFMPEG if Path(DEFAULT_FFMPEG).exists() else ""
    if not has_ffmpeg(ffmpeg_location if ffmpeg_location else None):
        print("[Peringatan] ffmpeg belum terdeteksi. Audio->MP3 / merge bisa gagal.")

    print("\nSumber URL:")
    print("1) Satu URL")
    print("2) Banyak URL (input manual)")
    print("3) Banyak URL dari file txt")
    src = input("Pilih [1/2/3]: ").strip() or "1"

    urls = []
    if src == "1":
        u = input("URL konten: ").strip()
        if u:
            urls = [u]
    elif src == "2":
        urls = get_urls_interactive()
    elif src == "3":
        fp = input("Path file txt URL: ").strip()
        urls = get_urls_from_file(fp)

    if not urls:
        print("Tidak ada URL.")
        return

    out = input("Folder output [downloads]: ").strip() or "downloads"
    cookies = input("Path cookies.txt (opsional, enter kalau tidak ada): ").strip() or None

    ff_in = input(f"Path ffmpeg bin (enter=default {'ON' if ffmpeg_location else 'OFF'}): ").strip()
    if ff_in:
        ffmpeg_location = ff_in

    print("\nPilih mode:")
    print("1) Video (auto, pilih resolusi + 60fps)")
    print("2) Audio MP3")
    print("3) Lihat format URL pertama dulu")
    mode = input("Mode [1/2/3]: ").strip() or "1"

    out_dir = Path(out)

    if mode == "3":
        info = get_info(urls[0], cookies)
        print(f"\nJudul sampel: {info.get('title','(tanpa judul)')}")
        list_top_formats(info)
        mode = input("Lanjut mode download [1/2]: ").strip() or "1"

    if mode == "2":
        for u in urls:
            download_audio(u, out_dir, cookies, ffmpeg_location)
        print("Selesai batch audio.")
        return

    res_in = input("Max resolusi [1080]: ").strip() or "1080"
    try:
        res = int(res_in)
    except ValueError:
        res = 1080

    fps60_in = input("Prioritaskan 60fps? [y/N]: ").strip().lower()
    prefer60 = fps60_in == "y"

    h264_in = input("Auto convert ke H.264 biar kebuka di semua player? [Y/n]: ").strip().lower()
    force_h264 = h264_in != "n"

    for u in urls:
        download_video(u, out_dir, res, prefer60, cookies, ffmpeg_location if ffmpeg_location else None, force_h264)

    print("Selesai batch video.")


if __name__ == "__main__":
    main()

