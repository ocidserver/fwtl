"""Salin data sqlite lokal -> Postgres (Supabase pooler). Idempotent: TRUNCATE dulu per tabel.

Usage: DATABASE_URL='postgresql://...' .venv/bin/python web/manage.py copydb
"""
import json
import sqlite3
from datetime import datetime, timezone

import psycopg
from psycopg.types.json import Jsonb
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from catalog.models import (Alternative, App, Category, CategoryRule,
                            RawPackage, SubCategory, SyncLog, WindowsApp)

BOOL_COLS = {"is_gui", "is_published", "is_staff", "is_active", "is_superuser"}
DT_COLS = {"updated_at", "started_at", "finished_at", "date_joined", "last_login"}
JSON_COLS = {"extra"}

TABLES = [
    (User, None),
    (Category, None),
    (WindowsApp, None),
    (App, None),
    (CategoryRule, None),
    (SubCategory, None),
    (RawPackage, None),
    (SyncLog, None),
    (App.categories.through, None),
    (App.subcategories.through, None),
    (Alternative, None),
]


def convert(col, val):
    if val is None:
        return None
    if col in BOOL_COLS:
        return bool(val)
    if col in DT_COLS:
        dt = val if isinstance(val, datetime) else datetime.fromisoformat(str(val).replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    if col in JSON_COLS:
        obj = val if isinstance(val, dict) else json.loads(val or "{}")
        return Jsonb(obj)
    return val


class Command(BaseCommand):
    help = "Copy sqlite -> Postgres (butuh DATABASE_URL ke Postgres)"

    def handle(self, *args, **opts):
        src = sqlite3.connect(str(settings.BASE_DIR / "db.sqlite3"))
        src.row_factory = sqlite3.Row
        db = settings.DATABASES["default"]
        assert db["ENGINE"].endswith("postgresql"), "DATABASE_URL harus Postgres!"
        pg = psycopg.connect(host=db["HOST"], port=db["PORT"], dbname=db["NAME"],
                             user=db["USER"], password=db["PASSWORD"], connect_timeout=30)
        pg.autocommit = True
        total = 0
        with pg.cursor() as cur:
            for model, _ in TABLES:
                table = model._meta.db_table
                cols = [f.column for f in model._meta.concrete_fields]
                col_list = ", ".join(f'"{c}"' for c in cols)
                rows = src.execute(f"SELECT {col_list} FROM {table}").fetchall()
                cur.execute(f'TRUNCATE "{table}" RESTART IDENTITY CASCADE')
                ph = ", ".join(["%s"] * len(cols))
                batch = []
                for r in rows:
                    batch.append(tuple(convert(c, r[c]) for c in cols))
                    if len(batch) >= 2000:
                        cur.executemany(f'INSERT INTO "{table}" ({col_list}) VALUES ({ph})', batch)
                        batch = []
                if batch:
                    cur.executemany(f'INSERT INTO "{table}" ({col_list}) VALUES ({ph})', batch)
                if rows:
                    cur.execute(f"SELECT setval(pg_get_serial_sequence('{table}','id'), (SELECT max(id) FROM \"{table}\"))")
                total += len(rows)
                self.stdout.write(f"  {table}: {len(rows)}")
        pg.close()
        self.stdout.write(self.style.SUCCESS(f"selesai copy total={total}"))
