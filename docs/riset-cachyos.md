# CachyOS Package Repository Extractor

Script Python untuk mengekstrak semua daftar package dari repository CachyOS (https://packages.cachyos.org/)

## Fitur

✓ Mengambil semua package dari CachyOS repository
✓ Mendukung filtering berdasarkan repository, architecture, atau search term
✓ Export ke format CSV dan JSON
✓ Informasi lengkap: nama, versi, repository, architecture, deskripsi, build date, size, dll
✓ Progress tracking dan statistik

## Data yang Dikumpulkan

Setiap package berisi informasi:
- **Name**: Nama package
- **Version**: Versi package
- **Repository**: Repository asal (extra, cachyos-extra-v4, dll)
- **Architecture**: Arsitektur (x86_64, x86_64_v3, x86_64_v4, any, dll)
- **Description**: Deskripsi package
- **Build Date**: Tanggal build (format readable dan Unix timestamp)
- **Installed Size**: Ukuran setelah instalasi (jika tersedia)
- **Compressed Size**: Ukuran terkompresi (jika tersedia)

## Instalasi

```bash
# Clone atau copy file ke direktori
cd /home/ocid/Code/cachyrepo

# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install requests
```

## Penggunaan

### Basic Usage - Ambil SEMUA packages

```bash
python cachyos_extractor.py
```

Kemudian tekan Enter saat diminta jumlah halaman (kosongkan untuk semua).

### Ambil Jumlah Halaman Tertentu

```bash
python cachyos_extractor.py
# Input: 10 (untuk 10 halaman)
# Input: 100 (untuk page_size)
```

### Estimasi Waktu

- **Page size 100**: ~381 halaman total, ~120 detik (2 menit) untuk semua
- **Page size 15**: ~2536 halaman total, ~510 detik (8-9 menit) untuk semua

Dengan rate limiting 0.2 detik per halaman.

## Output Files

Script akan menghasilkan 2 file:

1. **cachyos_packages_full.csv** - Format CSV untuk spreadsheet
2. **cachyos_packages_full.json** - Format JSON untuk processing

## Contoh Output

```
======================================================================
                 CachyOS Package Repository Extractor                 
======================================================================

Total packages tersedia: 38,039
Total halaman: 381 (dengan page_size=100)

✓ Page 1/381: 100 packages
✓ Page 2/381: 100 packages
...
✓ Page 381/381: 39 packages (Total: 38,039)

✓ Selesai! Total 38,039 packages berhasil diambil
  Waktu: 120.5 detik (2.0 menit)

Statistik:
  Jumlah packages per repository:
    extra: 15,234 packages
    cachyos-extra-v4: 8,123 packages
    ...
```

## Advanced Usage

### Modifikasi untuk Filtering Spesifik

Edit file `cachyos_extractor.py` dan ubah parameter di fungsi `get_packages()`:

```python
# Contoh: Hanya package dari repository "extra"
packages = extractor.extract_all(max_pages=None, page_size=100)

# Atau edit fungsi get_packages untuk menambahkan filter:
def get_packages(self, page=1, page_size=100, repo="extra", arch="x86_64"):
    # ... kode lainnya
```

## Struktur CSV Output

```csv
name,version,repository,architecture,description,build_date,build_date_unix,installed_size,compressed_size
firefox,122.0-1,extra,x86_64,Standalone web browser from mozilla.org,2026-01-19 10:30:15,1768800015,234567890,98765432
python,3.12.1-1,core,x86_64,Python programming language,2026-01-18 15:20:00,1768740000,123456789,45678901
```

## API Endpoint

Script ini menggunakan API endpoint resmi CachyOS:
```
GET https://packages.cachyos.org/api/search
```

Parameters:
- `current_page`: Nomor halaman (1-based)
- `page_size`: Jumlah item per halaman (default: 15, max: 100)
- `search`: Search term (optional)
- `repo`: Filter repository (optional)
- `arch`: Filter architecture (optional)

## Lisensi

Free to use and modify.

## Update

Last updated: 2026-01-20
Total packages di repository: 38,039

## Tips

1. Gunakan `page_size=100` untuk ekstraksi yang lebih cepat
2. Untuk dataset besar, pastikan koneksi internet stabil
3. Rate limiting sudah diterapkan (0.2s per request) untuk menghindari overload server
4. Jika ada error, coba jalankan ulang - script akan memulai dari awal

## Troubleshooting

### Error: Connection timeout
- Cek koneksi internet
- Coba kurangi page_size atau max_pages

### Error: Empty data
- Pastikan URL API masih valid: https://packages.cachyos.org/api/search
- Coba akses manual di browser

### Data tidak lengkap
- Beberapa field seperti `installed_size` dan `compressed_size` mungkin tidak tersedia untuk semua package
- Ini normal dan tergantung data dari repository

## Contact

Untuk pertanyaan atau masalah, silakan buat issue atau hubungi maintainer.
