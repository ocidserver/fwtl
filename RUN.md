# Menjalankan Dashboard 24 Jam (PC lokal + cloudflared)

## 1. Jalankan web (gunicorn, port 8000)

```bash
cd /home/ocid/Code/cachyrepo/web
SECRET_KEY="<isi-random-panjang>" \
DEBUG=0 \
ALLOWED_HOSTS="domain-kamu,localhost,127.0.0.1" \
CSRF_TRUSTED_ORIGINS="https://domain-kamu" \
BEHIND_CLOUDFLARE=1 \
../.venv/bin/gunicorn config.wsgi:application \
  --bind 127.0.0.1:8000 --workers 3 --daemon \
  --pid /tmp/opencode/dashboard.pid --log-file /tmp/opencode/dashboard.log
```

Cek: `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/`
Berhenti: `kill $(cat /tmp/opencode/dashboard.pid)`

Generate SECRET_KEY sekali saja:
```bash
../.venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 2. Tunnel via cloudflared (milikmu)

```bash
cloudflared tunnel --url http://127.0.0.1:8000
# atau tunnel bernama yang sudah ada, arahkan hostname ke http://127.0.0.1:8000
```

## 3. Sync data berkala (mingguan, opsional)

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
