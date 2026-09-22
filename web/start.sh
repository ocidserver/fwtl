#!/usr/bin/env bash
# FWTL - jalankan dashboard (satu perintah). Usage: ./start.sh
set -e
cd "$(dirname "$0")"

SECRET_FILE="${FWTL_SECRET_FILE:-$HOME/.config/fwtl/secret_key}"
if [ ! -f "$SECRET_FILE" ]; then
  mkdir -p "$(dirname "$SECRET_FILE")"
  ../.venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" > "$SECRET_FILE"
  chmod 600 "$SECRET_FILE"
  echo "secret baru dibuat di $SECRET_FILE"
fi

export SECRET_KEY="$(cat "$SECRET_FILE")"
export DEBUG=0
export ALLOWED_HOSTS="${ALLOWED_HOSTS:-localhost,127.0.0.1}"
export CSRF_TRUSTED_ORIGINS="${CSRF_TRUSTED_ORIGINS:-}"
export BEHIND_CLOUDFLARE=1

../.venv/bin/python manage.py migrate --noinput
../.venv/bin/python manage.py collectstatic --noinput >/dev/null

if [ -f /tmp/opencode/dashboard.pid ] && kill -0 "$(cat /tmp/opencode/dashboard.pid)" 2>/dev/null; then
  echo "sudah berjalan (pid $(cat /tmp/opencode/dashboard.pid))"
else
  ../.venv/bin/gunicorn config.wsgi:application \
    --bind 127.0.0.1:8000 --workers 3 --daemon \
    --pid /tmp/opencode/dashboard.pid --log-file /tmp/opencode/dashboard.log
  sleep 4
  curl -s -o /dev/null -w "FWTL: %{http_code}\n" --max-time 15 http://127.0.0.1:8000/
fi
