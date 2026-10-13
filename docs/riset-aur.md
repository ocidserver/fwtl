# AUR Scraper Documentation

## Overview
Script ini mengambil semua data paket dari AUR (Arch User Repository) menggunakan AUR RPC API.

## Files Generated

### 1. aur_packages_full.csv (35 MB)
CSV file yang berisi informasi lengkap untuk 104,358+ paket AUR dengan kolom:
- **name**: Nama paket
- **version**: Versi paket
- **description**: Deskripsi paket
- **maintainer**: Nama maintainer (kosong jika orphaned)
- **votes**: Jumlah votes dari user
- **popularity**: Skor popularitas paket
- **first_submitted**: Tanggal pertama kali paket disubmit (format: YYYY-MM-DD HH:MM:SS)
- **first_submitted_unix**: Unix timestamp
- **last_modified**: Tanggal terakhir dimodifikasi
- **last_modified_unix**: Unix timestamp
- **out_of_date**: Tanggal ditandai out-of-date (kosong jika tidak)
- **out_of_date_unix**: Unix timestamp
- **url**: URL upstream project
- **package_base**: Nama package base
- **package_base_id**: ID package base
- **id**: ID paket di AUR
- **keywords**: Keywords (dipisah dengan |)
- **license**: Lisensi (dipisah dengan |)
- **depends**: Dependencies (dipisah dengan |)
- **makedepends**: Build dependencies (dipisah dengan |)
- **optdepends**: Optional dependencies (dipisah dengan |)
- **conflicts**: Paket yang conflict (dipisah dengan |)
- **provides**: Paket yang diprovide (dipisah dengan |)
- **replaces**: Paket yang digantikan (dipisah dengan |)

### 2. aur_packages_full.json (86 MB)
Backup dalam format JSON dengan struktur data yang sama.

### 3. cachyos_aur_comparison.csv
Perbandingan paket yang ada di CachyOS dan AUR, menunjukkan 570 paket yang overlap.

## Scripts

### aur_scraper.py
Script utama untuk mengambil data dari AUR.

**Features:**
- Menggunakan AUR RPC API untuk efisiensi
- Batch processing (100 paket per request)
- Rate limiting untuk tidak membebani server AUR
- Progress tracking
- Error handling

**Cara penggunaan:**
```bash
python aur_scraper.py
```

**Waktu eksekusi:** ~28 menit untuk 104,358+ paket

### aur_stats.py
Menampilkan statistik data AUR yang telah diambil.

**Output:**
- Total packages
- Statistik votes (total, average, median, max)
- Statistik popularity
- Top 10 packages by votes
- Top 10 packages by popularity
- Jumlah orphaned packages
- Jumlah out-of-date packages

**Cara penggunaan:**
```bash
python aur_stats.py
```

### compare_cachyos_aur.py
Membandingkan paket CachyOS dengan AUR.

**Output:**
- Jumlah overlap packages
- Top 20 popular packages yang ada di kedua repo
- File CSV dengan full comparison

**Cara penggunaan:**
```bash
python compare_cachyos_aur.py
```

## Statistics

### AUR Repository Statistics
- **Total Packages**: 104,358
- **Packages with maintainer**: 89,251 (85.5%)
- **Orphaned packages**: 15,107 (14.5%)
- **Out-of-date packages**: 9,872 (9.5%)
- **Total Votes**: 474,034
- **Average Votes**: 4.54
- **Median Votes**: 1.00

### Top 10 Most Voted Packages
1. **yay** (2,481 votes) - Yet another yogurt. Pacman wrapper and AUR helper
2. **dropbox** (2,381 votes) - File synchronization service
3. **google-chrome** (2,321 votes) - Google's web browser
4. **ttf-ms-fonts** (2,166 votes) - Microsoft TrueType fonts
5. **octopi** (1,915 votes) - Powerful Pacman frontend
6. **visual-studio-code-bin** (1,603 votes) - VS Code editor
7. **teamviewer** (1,487 votes) - Remote desktop software
8. **android-sdk** (1,481 votes) - Android development SDK
9. **virtualbox-ext-oracle** (1,371 votes) - VirtualBox extension pack
10. **tor-browser-bin** (1,299 votes) - Anonymous web browser

### Top 10 Most Popular Packages
1. **yay** (38.61 popularity)
2. **nvidia-580xx-utils** (31.58 popularity)
3. **opencl-nvidia-580xx** (31.58 popularity)
4. **nvidia-580xx-dkms** (31.58 popularity)
5. **paru** (29.64 popularity)
6. **qt-sudo** (28.57 popularity)
7. **visual-studio-code-bin** (28.53 popularity)
8. **octopi** (27.68 popularity)
9. **brave-bin** (23.28 popularity)
10. **zen-browser-bin** (22.21 popularity)

### CachyOS vs AUR Overlap
- **Total CachyOS packages**: 15,579
- **Total AUR packages**: 104,358
- **Packages in both**: 570 (3.7% of CachyOS)
- **CachyOS-only packages**: 15,009 (96.3%)

## API Information

**AUR RPC Endpoint**: https://aur.archlinux.org/rpc

**Methods Used:**
- `packages.gz` - Daftar semua nama paket (compressed)
- `type=multiinfo` - Mendapatkan info detail untuk multiple paket sekaligus

**Rate Limiting:**
- 0.3 detik delay antara setiap batch request
- 100 paket per batch untuk efisiensi

## Data Sources
- **AUR**: https://aur.archlinux.org/
- **AUR RPC Documentation**: https://aur.archlinux.org/rpc/
- **Package List**: https://aur.archlinux.org/packages.gz

## Notes

1. **Votes vs Popularity**: 
   - Votes adalah jumlah user yang memberikan vote
   - Popularity adalah weighted score berdasarkan usage dan waktu

2. **Orphaned Packages**: 
   - Paket tanpa maintainer (field maintainer kosong)
   - User dapat adopt paket orphaned ini

3. **Out-of-Date Packages**:
   - Paket yang ditandai out-of-date oleh user
   - Maintainer perlu update ke versi terbaru

4. **Data Freshness**:
   - Data diambil pada: 21 Januari 2026
   - Untuk data terbaru, jalankan ulang `aur_scraper.py`

## Dependencies

```bash
pip install requests beautifulsoup4
```

## License
Script ini dibuat untuk keperluan analisis dan research.
