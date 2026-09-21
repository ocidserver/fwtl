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

## Fase 2 — Normalisasi & pengelompokan [SELESAI]
- [x] Tabel kanonis `App`: 162.464 raw → 117.379 App lintas sumber (cth: `firefox`+`firefox-bin`+`org.mozilla.firefox` → 1 App "Firefox")
- [x] Rules kategori dari `package_classifier.py` → 30 kategori + 321 `CategoryRule`; 205.440 relasi
- [x] Tandai `is_gui`: 91.736 GUI / 25.643 non-GUI (libs, fonts, *-dev disembunyikan dari UI nanti)
- [x] Review internal: distribusi + sampel merge OK. Catatan kualitas: keyword substring terlalu longgar (`tar`→`avatar`, `go`→`mongo`) sehingga `development-tools` 56rb & `archive-compression` 15rb kemungkinan over-match — perbaiki dengan word-boundary/allowlist di iterasi berikutnya
- [ ] Halaman review internal hasil grouping sebelum publik (pindah ke Fase 4 sebagai admin view)

## Fase 3 — Rekomendasi Windows [SELESAI]
- [x] Seed 125 `WindowsApp` dari `windows_alt` classifier (29 kategori)
- [x] 111 `Alternative` kurasi dengan kompatibilitas + catatan ID/EN + perintah install per sumber (pacman/yay/flatpak otomatis dari `RawPackage`)
- [x] Panduan `windows_migration_guide.txt` tergantikan data terstruktur (query-able per Windows app)

## Fase 4 — Web publik MVP (ID/EN) [SELESAI]
- [x] Halaman: home/search, `/apps`, `/kategori/<slug>`, `/windows/<slug>`, `/app/<slug>` (semua 200 OK)
- [x] Search sederhana `icontains` (SQLite; FTS Postgres dijadwalkan saat migrasi DB)
- [x] Switcher bahasa ID/EN (`i18n_patterns`, `set_language`), string UI via `gettext` + `.mo` terkompilasi, konten via field `_id/_en`, `hreflang` + `sitemap.xml`
- [x] Produksi lokal: gunicorn + WhiteNoise + `collectstatic` OK, flag `BEHIND_CLOUDFLARE`, baca `RUN.md`

## Fase 5 — Polish & deploy
- [ ] Dockerfile + deploy (Fly.io/Render/VPS), backup DB, alert sync gagal
- [ ] API read-only `/api/`, cache halaman populer
- [ ] Dokumentasi: gabung 3 README lama jadi `docs/`

## Keputusan yang sudah diambil
- Django (bukan Flask) — butuh admin kurasi + SEO pages cepat
- Postgres (bukan SQLite) — butuh FTS + konkurensi tulis ETL
- ID default, EN kedua; konten model duplikat `_id/_en`

## Cara eksekusi
Kerjakan berurutan per checkbox, commit per sub-fase, jangan loncat ke web sebelum ingestion stabil.
