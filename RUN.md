# Menjalankan Dashboard 24 Jam (PC lokal + cloudflared)

## 1. Jalankan web (satu perintah)

```bash
cd /home/ocid/Code/cachyrepo/web
./start.sh
```

`start.sh` mengurus: secret key (`~/.config/fwtl/secret_key`, dibuat sekali),
migrasi, `collectstatic`, lalu gunicorn daemon di `127.0.0.1:8000`.
Cek: `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/`
Berhenti: `kill $(cat /tmp/opencode/dashboard.pid)`

Untuk domain sendiri:

```bash
ALLOWED_HOSTS="domain-kamu,localhost,127.0.0.1" \
CSRF_TRUSTED_ORIGINS="https://domain-kamu" ./start.sh
```

## 2. Tunnel via cloudflared (milikmu)

```bash
cloudflared tunnel --url http://127.0.0.1:8000
# atau tunnel bernama yang sudah ada, arahkan hostname ke http://127.0.0.1:8000
```

## 3. Sync data berkala (mingguan, opsional)

> **Matikan web dulu** — job tulis mengunci SQLite:
> `kill $(cat /tmp/opencode/dashboard.pid)` — nyalakan lagi setelah selesai (perintah no. 1).

```bash
cd /home/ocid/Code/cachyrepo
.venv/bin/python web/manage.py sync_cachyos
.venv/bin/python web/manage.py sync_aur
.venv/bin/python web/manage.py sync_flathub
.venv/bin/python web/manage.py build_apps
.venv/bin/python web/manage.py seed_windows
```

## Catatan

- DB masih SQLite (`web/db.sqlite3`, ~103MB). Jangan jalankan sync saat
  traffic padat — tulis SQLite mengunci DB. Migrasi Postgres dijadwalkan
  bila dibutuhkan (lihat plan.md Fase 5).
- Admin: buat superuser dulu — `.venv/bin/python web/manage.py createsuperuser`
