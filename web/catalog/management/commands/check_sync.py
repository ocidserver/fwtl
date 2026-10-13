"""Alert sync: tampilkan SyncLog gagal/terbaru; exit 1 bila ada yg gagal <--jam jam.

Usage: .venv/bin/python web/manage.py check_sync [--jam 168]
Dipakai operator setelah rangkaian sync / via cron PC.
"""
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from catalog.models import SyncLog


class Command(BaseCommand):
    help = "Cek status sync terakhir (alert bila gagal)"

    def add_arguments(self, parser):
        parser.add_argument("--jam", type=int, default=168)

    def handle(self, *args, **opts):
        since = timezone.now() - timedelta(hours=opts["jam"])
        logs = SyncLog.objects.filter(started_at__gte=since).order_by("-started_at")
        failed = [l for l in logs if l.status not in ("done",)]
        for l in logs[:15]:
            self.stdout.write(f"{l.started_at:%m-%d %H:%M} {l.source:8} {l.status:8} total={l.total}")
        if failed:
            self.stderr.write(f"ALERT: {len(failed)} sync bermasalah dalam {opts['jam']} jam terakhir")
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS("semua sync OK"))
