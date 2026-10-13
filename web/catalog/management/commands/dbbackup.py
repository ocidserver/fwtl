"""Backup logis Postgres -> JSONL per tabel (streaming, hemat memori).

Usage: DATABASE_URL='...' .venv/bin/python web/manage.py dbbackup --dest ~/backup/fwtl
Hasil: ~/backup/fwtl/YYYYMMDD-HHMMSS/<tabel>.jsonl.gz
"""
import gzip
import json
from datetime import datetime
from pathlib import Path

import psycopg
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Backup Postgres ke JSONL.gz per tabel"

    def add_arguments(self, parser):
        parser.add_argument("--dest", default=str(Path.home() / "backup" / "fwtl"))

    def handle(self, *args, **opts):
        db = settings.DATABASES["default"]
        assert db["ENGINE"].endswith("postgresql"), "DATABASE_URL harus Postgres!"
        outdir = Path(opts["dest"]) / datetime.now().strftime("%Y%m%d-%H%M%S")
        outdir.mkdir(parents=True, exist_ok=True)
        pg = psycopg.connect(host=db["HOST"], port=db["PORT"], dbname=db["NAME"],
                             user=db["USER"], password=db["PASSWORD"], connect_timeout=30)
        total = 0
        with pg.cursor() as cur:
            tables = [r[0] for r in cur.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY 1").fetchall()]
            for t in tables:
                cols = [r[0] for r in cur.execute(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name=%s ORDER BY ordinal_position", (t,)).fetchall()]
                n = 0
                with gzip.open(outdir / f"{t}.jsonl.gz", "wt") as f:
                    stream = cur.stream(f'SELECT {", ".join(chr(34)+c+chr(34) for c in cols)} FROM "{t}"')
                    for row in stream:
                        f.write(json.dumps(dict(zip(cols, row)), default=str) + "\n")
                        n += 1
                total += n
                self.stdout.write(f"  {t}: {n}")
        pg.close()
        self.stdout.write(self.style.SUCCESS(f"backup ke {outdir} total={total}"))
