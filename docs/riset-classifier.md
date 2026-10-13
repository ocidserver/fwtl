# CachyOS Package Classifier

## 📦 Apa ini?

Tool untuk mengklasifikasikan 5000+ packages CachyOS ke dalam kategori-kategori yang mudah dipahami, khususnya untuk membantu migrasi dari **Windows ke Linux**.

## ✅ Fitur

- ✓ Klasifikasi otomatis 5000+ packages ke 29 kategori
- ✓ Panduan migrasi Windows → CachyOS Linux
- ✓ Mapping aplikasi Windows ke alternatif Linux
- ✓ Export per kategori (CSV)
- ✓ Laporan lengkap dengan deskripsi

## 📂 File Output

### 1. **windows_migration_guide.txt** (PALING PENTING!)
Panduan lengkap untuk pengguna Windows yang ingin migrasi ke CachyOS.

**Berisi:**
- Daftar aplikasi Windows yang umum digunakan
- Alternatif aplikasi di CachyOS Linux
- Perintah instalasi (`sudo pacman -S nama-package`)
- Tips dan trik migrasi

**Preview:**
```
📦 WEB BROWSER
🪟 Windows: Google Chrome, Firefox, Edge, Opera, Brave
🐧 Linux: chromium, firefox, brave-bin, opera, falkon

📦 OFFICE & PRODUCTIVITY  
🪟 Windows: Microsoft Office, Adobe Acrobat, Notepad++
🐧 Linux: libreoffice, okular, kate, onlyoffice, wps-office

📦 GAMING
🪟 Windows: Steam, Epic Games, GOG
🐧 Linux: steam, lutris, heroic-games-launcher, wine, proton
```

### 2. **category_report.txt**
Laporan teknis lengkap per kategori dengan detail packages.

### 3. **category_*.csv** (29 files)
CSV terpisah per kategori untuk analisis lebih lanjut:
- `category_web_browser.csv` - 214 packages
- `category_gaming.csv` - 81 packages
- `category_office___productivity.csv` - 80 packages
- `category_development_tools.csv` - 527 packages
- dll...

## 🎯 Kategori yang Tersedia

| No | Kategori | Packages | Deskripsi |
|----|----------|----------|-----------|
| 1 | Development Tools | 527 | Compiler, Python, Git, IDE |
| 2 | Libraries & Dependencies | 476 | System libraries |
| 3 | Archive & Compression | 371 | zip, tar, 7z, rar |
| 4 | System Utilities | 303 | System tools & monitors |
| 5 | Web Browser | 214 | Firefox, Chrome, Brave, dll |
| 6 | Security & Privacy | 181 | VPN, firewall, encryption |
| 7 | Desktop Environment | 125 | KDE, GNOME, XFCE |
| 8 | Database | 108 | MySQL, PostgreSQL, MongoDB |
| 9 | Web Development | 102 | Apache, nginx, PHP |
| 10 | Text Editor & IDE | 99 | Vim, VSCode, Emacs |
| 11 | Gaming | 81 | Steam, Wine, Proton |
| 12 | Office & Productivity | 80 | LibreOffice, PDF tools |
| 13 | Graphics & Image Editing | 78 | GIMP, Inkscape, Krita |
| 14 | Terminal & Shell | 67 | Bash, Zsh, Fish, Alacritty |
| 15 | Media Player & Video | 65 | VLC, MPV, FFmpeg |
| 16 | Audio & Music | 64 | PulseAudio, Audacity |
| 17 | Networking | 56 | Wireshark, nmap |
| 18 | Virtualization | 39 | QEMU, Docker, VirtualBox |
| 19 | Cloud & Sync | 26 | Nextcloud, Syncthing |
| 20 | Communication & Chat | 26 | Discord, Telegram |
| 21 | Scientific & Math | 23 | LaTeX, Octave |
| 22 | Printing & Scanning | 23 | CUPS, SANE |
| 23 | CAD & 3D Modeling | 19 | FreeCAD, Blender |
| 24 | Download Manager | 10 | wget, aria2, qBittorrent |
| 25 | Email Client | 10 | Thunderbird, Evolution |
| 26 | Fonts & Typography | 10 | System fonts |
| 27 | File Manager | 8 | Dolphin, Nautilus |
| 28 | Remote Desktop & VNC | 9 | RDP, VNC, NoMachine |
| 29 | Other | 494 | Miscellaneous |

## 🚀 Cara Menggunakan

### Untuk User (Membaca Hasil)

```bash
# Baca panduan migrasi Windows
less windows_migration_guide.txt

# Atau buka dengan text editor
kate windows_migration_guide.txt
```

### Untuk Developer (Regenerate)

```bash
# 1. Ekstrak data packages terlebih dahulu
python cachyos_extractor.py
# Input: berapa halaman yang ingin diambil

# 2. Jalankan classifier
python package_classifier.py
```

## 💡 Contoh Penggunaan

### Saya butuh alternatif Photoshop
```bash
# Lihat di windows_migration_guide.txt bagian "Graphics & Image Editing"
# Atau cek file:
cat category_graphics___image_editing.csv
```

**Alternatif:**
- GIMP (gratis, mirip Photoshop)
- Krita (untuk digital painting)
- Inkscape (untuk vector graphics)

### Saya butuh aplikasi untuk office work
```bash
cat category_office___productivity.csv
```

**Alternatif:**
- LibreOffice (gratis, kompatibel MS Office)
- OnlyOffice (interface mirip MS Office)
- WPS Office (closed source, sangat mirip MS Office)

### Saya gamer, apa yang tersedia?
```bash
cat category_gaming.csv
```

**Tersedia:**
- Steam (native Linux)
- Lutris (game launcher)
- Wine/Proton (jalankan game Windows)
- GameMode (optimasi gaming)
- MangoHud (FPS overlay)

## 📋 Mapping Windows → Linux (Popular)

| Windows App | CachyOS Alternative | Compatibility |
|-------------|---------------------|---------------|
| **Browser** | | |
| Google Chrome | chromium, google-chrome | 100% |
| Firefox | firefox | 100% |
| Edge | microsoft-edge-stable | 100% |
| **Office** | | |
| MS Office | libreoffice-fresh | 95% |
| Adobe Acrobat | okular, evince | 90% |
| Notepad++ | kate, gedit, vim | 100% |
| **Media** | | |
| VLC | vlc | 100% |
| Photoshop | gimp, krita | 70-80% |
| Premiere | kdenlive, davinci-resolve | 70-85% |
| **Gaming** | | |
| Steam | steam | 100% |
| Epic Games | heroic-games-launcher | 90% |
| **Dev Tools** | | |
| VS Code | code | 100% |
| Visual Studio | qt-creator, kdevelop | 70% |
| Git | git | 100% |
| **Communication** | | |
| Discord | discord | 100% |
| Slack | slack-desktop | 100% |
| Teams | teams | 95% |
| Zoom | zoom | 100% |

## 🎓 Tips Migrasi dari Windows

### 1. **Format File Kompatibel**
- Dokumen: .docx, .xlsx, .pptx ✓
- Media: .mp3, .mp4, .avi, .mkv ✓
- Gambar: .jpg, .png, .gif, .psd (partial) ✓
- Archive: .zip, .rar, .7z ✓

### 2. **Gaming di Linux**
- Steam Proton: 80%+ game Windows berjalan di Linux
- Lutris: Install game dari berbagai platform
- Wine: Jalankan aplikasi Windows

### 3. **Software Berbayar**
Kebanyakan alternatif Linux adalah **GRATIS & Open Source**:
- Photoshop ($) → GIMP (Gratis)
- Office 365 ($) → LibreOffice (Gratis)
- Premiere ($) → Kdenlive (Gratis)

### 4. **Install Packages**
```bash
# Cari package
pacman -Ss nama-app

# Install
sudo pacman -S nama-package

# Update sistem
sudo pacman -Syu
```

## 📊 Statistik

- **Total packages**: 5,000
- **Unique applications**: ~3,000
- **Categories**: 29
- **Repositories**: extra, cachyos, cachyos-v3, cachyos-v4, dll
- **Architectures**: x86_64, x86_64_v3, x86_64_v4, any

## 🔄 Update

Untuk mendapatkan data terbaru:

```bash
# 1. Ekstrak data terbaru
python cachyos_extractor.py

# 2. Re-classify
python package_classifier.py
```

## 📞 Support

- CachyOS Wiki: https://wiki.cachyos.org/
- Forum: https://discuss.cachyos.org/
- Package Search: https://packages.cachyos.org/

## 📝 Lisensi

Open source - bebas digunakan dan dimodifikasi.

---

**Selamat Migrasi ke CachyOS Linux! 🐧**
