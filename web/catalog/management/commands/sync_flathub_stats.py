import time
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from catalog.models import RawPackage, Source, SyncLog


STATS_URL = "https://flathub.org/api/v2/stats/{appid}"


class Command(BaseCommand):
    help = "Ambil installs_total Flathub per app, simpan di extra.downloads"

    def add_arguments(self, parser):
        parser.add_argument("--delay", type=float, default=0.1)

    def handle(self, *args, **opts):
        delay = opts["delay"]
        log = SyncLog.objects.create(source=Source.FLATHUB, message="stats")
        session = requests.Session()
        session.headers.update({"User-Agent": "MigrasiLinux/1.0"})
        ids = list(RawPackage.objects.filter(source=Source.FLATHUB).values_list("id", "name"))
        self.stdout.write(f"Total {len(ids)} app")

        batch, done, fail = [], 0, 0
        for i, (rid, appid) in enumerate(ids, 1):
            try:
                r = session.get(STATS_URL.format(appid=appid), timeout=20)
                if r.status_code == 200:
                    total = r.json().get("installs_total", 0)
                    batch.append((rid, total))
                else:
                    fail += 1
            except Exception:
                fail += 1
            time.sleep(delay)
            if len(batch) >= 200:
                done += self._flush(batch)
                batch = []
            if i % 500 == 0:
                self.stdout.write(f"  {i}/{len(ids)} ok={done} gagal={fail}")
        if batch:
            done += self._flush(batch)

        log.total, log.inserted, log.updated = len(ids), done, 0
        log.status = "done"
        log.finished_at = timezone.now()
        log.save()
        self.stdout.write(self.style.SUCCESS(f"selesai ok={done} gagal={fail}"))

    def _flush(self, batch):
        objs = []
        for rid, total in batch:
            try:
                o = RawPackage.objects.only("extra").get(id=rid)
            except RawPackage.DoesNotExist:
                continue
            ex = dict(o.extra or {})
            ex["downloads"] = total
            o.extra = ex
            objs.append(o)
        RawPackage.objects.bulk_update(objs, ["extra"], batch_size=200)
        return len(objs)
