# DownCLI Suite (FB / IG / YT)

## Clone dari GitHub

Repo name: **medsos-downloader**

```bash
git clone https://github.com/indrafata980/medsos-downloader.git
cd medsos-downloader
```



---
## Isi folder
- `down_video.py` → download **video** (prioritas 60fps, fallback otomatis), auto convert ke **H.264**, hasil final 1 file.
- `down_music.py` → download **audio** jadi **MP3**.
- `downcli_menu.py` → mode interaktif (single/batch, video/audio, list format).
- `requirements.txt` → dependency Python.
- `setup.bat` → setup otomatis di Windows.
- `setup.sh` → setup otomatis di Termux.

---

## Platform yang didukung
- ✅ YouTube
- ✅ Facebook (video/reel)
- ✅ Instagram (post/reel)

> Catatan: konten private/terbatas login bisa butuh `cookies.txt` (khusus di `downcli_menu.py`).

---

## 1) Setup Windows (CMD)

```bat
cd /d D:\download\downcli_suite
setup.bat
```

Kalau `ffmpeg` belum ada di PATH, install dulu atau pakai path ffmpeg di script.

---

\n> Catatan Termux: jangan jalankan pip install -U pip karena akan error Installing pip is forbidden.\n\n```bash
cd ~/downcli_suite
chmod +x setup.sh
./setup.sh
```

---

## Pintasan perintah di Termux (`custom`, `video`, `music`)

Buat command sekali aja:

```bash
# custom -> buka menu interaktif
echo 'cd /data/data/com.termux/files/home/downcli_suite && python downcli_menu.py' > /data/data/com.termux/files/usr/bin/custom
chmod +x /data/data/com.termux/files/usr/bin/custom

# video -> langsung downloader video
echo 'cd /data/data/com.termux/files/home/downcli_suite && python down_video.py' > /data/data/com.termux/files/usr/bin/video
chmod +x /data/data/com.termux/files/usr/bin/video

# music -> langsung downloader music
echo 'cd /data/data/com.termux/files/home/downcli_suite && python down_music.py' > /data/data/com.termux/files/usr/bin/music
chmod +x /data/data/com.termux/files/usr/bin/music
```

Cara pakai:

```bash
custom
video
music
```

---
### A. Download video (langsung)
```bash
python down_video.py
```
Lalu paste URL FB/IG/YT.

Perilaku:
- pilih kualitas tertinggi yang tersedia
- prioritas 60fps (kalau ada)
- fallback otomatis kalau 60fps tidak tersedia
- hasil final auto convert ke H.264 (lebih kompatibel player)

### B. Download audio MP3 (langsung)
```bash
python down_music.py
```
Lalu paste URL FB/IG/YT.

### C. Menu interaktif (lengkap)
```bash
python downcli_menu.py
```
Fitur:
- satu URL / banyak URL
- dari input manual atau file `.txt`
- mode video/audio
- list format tersedia

---

## 4) Lokasi hasil download
Default disimpan ke folder:
- `downloads/` (di folder tempat script dijalankan)

Contoh Windows:
- `D:\download\downcli_suite\downloads`

Contoh Termux:
- `~/downcli_suite/downloads`

---

## 5) Format file output
- Video final: `YYYYMMDD_PLATFORM_ID.mp4`
- Audio final: `YYYYMMDD_PLATFORM_ID.mp3`

Contoh `PLATFORM`:
- `YT` (YouTube)
- `FB` (Facebook)
- `IG` (Instagram)

---

## 6) Troubleshooting

### Error: `ffmpeg / ffprobe not found`
- Pastikan ffmpeg terinstall dan bisa dipanggil (`ffmpeg -version`)
- Atau set path ffmpeg di script (`DEFAULT_FFMPEG`)

### Error IG/FB format tidak tersedia
- Coba ulang (platform sering ubah format)
- Gunakan mode menu lalu list format dulu
- Untuk konten private, gunakan cookies di `downcli_menu.py`

### Error JS runtime warning (yt-dlp)
- Umumnya warning, bukan fatal.
- Script sudah set runtime fallback (`deno,node,bun,quickjs`).

---

## 7) Catatan penggunaan
Gunakan hanya untuk konten yang kamu punya izin akses/unduh, dan patuhi aturan platform setempat.



