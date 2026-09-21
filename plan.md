# Rencana Pengembangan — Dashboard Migrasi Windows → Linux (CachyOS)

Tujuan: dashboard publik multi-bahasa (ID/EN) yang menghimpun semua aplikasi dari
`packages.cachyos.org`, AUR, dan Flatpak/Flathub, mengelompokkannya, lalu memberi
rekomendasi alternatif untuk setiap aplikasi Windows populer.

Stack pilihan: **Django + Postgres + Templates + HTMX** (alasan: admin kurasi gratis,
SEO-friendly, cocok untuk solo dev; lihat diskusi sebelumnya).

## Status
- [x] Riset/scraper lama (CachyOS ~38rb, AUR ~104rb paket) + classifier keyword 29 kategori
- [ ] Fase 0 — Fondasi
- [x] Fase 1 — Ingestion (CachyOS, AUR, Flathub)
- [x] Fase 2 — Normalisasi & pengelompokan
- [x] Fase 3 — Rekomendasi Windows
- [x] Fase 4 — Web publik MVP
- [ ] Fase 5 — Polish & deploy

---

## Fase 0 — Fondasi [SELESAI]
- [x] `git init` + `.gitignore` (data besar `*.csv/*.json/*.db` tetap ignore, hanya seed kecil di repo)
- [x] Struktur proyek Django baru terpisah dari script riset (`web/` atau repo baru), script lama jadi referensi ETL
- [x] Docker Compose: `web + postgres`
- [x] Settings i18n: `LANGUAGE_CODE='id'`, `LANGUAGES=[id,en]`, `LocaleMiddleware`, `USE_I18N=True`
- [x] Model dasar: `Source`, `RawPackage`, `App`, `Category`, `WindowsApp`, `Alternative`, `SyncLog`
- [x] Django Admin terdaftar untuk semua model di atas

## Fase 1 — Ingestion lengkap [SELESAI]
### 1a. CachyOS (`packages.cachyos.org/api/search`)
- [x] Port `cachyos_extractor.py` → `manage.py sync_cachyos`
- [x] Incremental by `build_date_unix`, retry/backoff + resume checkpoint
- [x] Simpan ke `RawPackage(source=cachyos)` + tulis `SyncLog`
- [x] Full sync semua halaman (~380 hal, ~2 mnt) — SELESAI: 397 hal, 39.602 entri (29.797 insert + 9.805 update), 39.393 row unik di DB
### 1b. AUR (`packages.gz` + RPC `multiinfo`)
- [x] Port `aur_scraper.py` → `manage.py sync_aur` (batch 100, bulk upsert, retry)
- [x] Uji `--max-batches 2` OK (200/200 insert; total AUR kini 119.744 paket)
- [x] Full sync (~1.200 batch) — SELESAI: 1.198 batch, 119.744 total (119.544 insert + 200 update)
### 1c. Flathub (baru)
- [x] `manage.py sync_flathub` (daftar ID + detail per app via `/api/v2/appstream`, bulk upsert)
- [x] Uji `--max-apps 5` OK (5/5 insert; total 3.327 aplikasi)
- [x] Full sync (~3.327 app) — SELESAI: 3.327 total (3.322 insert + 5 update)
**Total DB: 162.464 row (CachyOS 39.393 + AUR 119.744 + Flathub 3.327)**
- [ ] Scheduler mingguan (cron/celery-beat) + diff report

## Fase 2 — Normalisasi & pengelompokan [SELESAI + SUBKATEGORI]
- [x] Tabel kanonis `App`: 162.464 raw → 117.379 App lintas sumber
- [x] Rules kategori → 30 kategori; `reclassify` (word-boundary + names-only + strip sufiks): dev-tools 56rb→21,7rb, firefox→browser, 0verkill→gaming
- [x] 108 `SubCategory` (3-5 per kategori) + `assign_subcategories`; halaman `/kategori/<cat>/<sub>/`, kategori dikelompokkan per sub
- [x] Tandai `is_gui`: 91.736 GUI / 25.643 non-GUI

## Fase 3 — Rekomendasi Windows [SELESAI]
- [x] Seed 125 `WindowsApp` dari `windows_alt` classifier (29 kategori)
- [x] 111 `Alternative` kurasi dengan kompatibilitas + catatan ID/EN + perintah install per sumber (pacman/yay/flatpak otomatis dari `RawPackage`)
- [x] Panduan `windows_migration_guide.txt` tergantikan data terstruktur (query-able per Windows app)

## Fase 4 — Web publik MVP (ID/EN) [SELESAI + ITERASI DOCS]
- [x] Halaman: home/search, `/apps`, `/kategori/<slug>`, `/windows/<slug>`, `/app/<slug>` (semua 200 OK)
- [x] Layout dokumentasi ala FMHY: sidebar kiri (Jelajah + 30 Kategori + Dokumentasi), konten utama, responsif
- [x] Detail aplikasi lengkap: votes, popularity, unduhan Flathub, maintainer, lisensi, developer, homepage, perintah install per sumber, tabel paket
- [x] `/top/`: AUR by votes, AUR by popularity, Flathub by unduhan, paling sering jadi pengganti
- [x] Dokumentasi: `/docs/install|migrasi|sumber-data|faq` (ID/EN)
- [x] Search sederhana `icontains` (SQLite; FTS Postgres dijadwalkan saat migrasi DB)
- [x] Switcher bahasa ID/EN (`i18n_patterns`, `set_language`), string UI via `gettext` + `.mo` terkompilasi, konten via field `_id/_en`, `hreflang` + `sitemap.xml`
- [x] Produksi lokal: gunicorn + WhiteNoise + `collectstatic` OK, flag `BEHIND_CLOUDFLARE`, baca `RUN.md`
- [x] `sync_flathub_stats` (installs_total → extra.downloads) — SELESAI: 3.325/3.327 app (Firefox 12,2 jt, Chrome 12,1 jt)

## Fase 5 — Polish & deploy
- [ ] Dockerfile + deploy (Fly.io/Render/VPS), backup DB, alert sync gagal
- [ ] API read-only `/api/`, cache halaman populer
- [ ] Dokumentasi: gabung 3 README lama jadi `docs/`

## Keputusan yang sudah diambil
- Django (bukan Flask) — butuh admin kurasi + SEO pages cepat
- Postgres (bukan SQLite) — butuh FTS + konkurensi tulis ETL
- ID default, EN kedua; konten model duplikat `_id/_en`

## Catatan operasional
- Job tulis panjang (`sync_*`, `build_apps`, `reclassify`, `assign_*`) harus jalan saat
  web MATI — SQLite mengunci DB dan job bisa gagal di tengah (pernah merusak
  relasi kategori; recovery: matikan web, ulangi job). Lihat `RUN.md`.
- Klasifikasi keyword punya batas inheren (kata umum di deskripsi). Perbaikan
  yang sudah diterapkan: word-boundary utk keyword ≤3 huruf, keyword pendek
  hanya di nama paket, strip sufiks `-git/-bin/dll`.
