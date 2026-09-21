import gzip
import time
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from catalog.models import RawPackage, Source, SyncLog


RPC_URL = "https://aur.archlinux.org/rpc"
PACKAGES_GZ = "https://aur.archlinux.org/packages.gz"


class Command(BaseCommand):
    help = "Sync paket AUR ke RawPackage (packages.gz + RPC multiinfo, bulk upsert)"

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=100)
        parser.add_argument("--delay", type=float, default=0.3)
        parser.add_argument("--max-batches", type=int, default=0)

    def handle(self, *args, **opts):
        batch_size = opts["batch_size"]
        delay = opts["delay"]
        max_batches = opts["max_batches"] or None
        log = SyncLog.objects.create(source=Source.AUR)
        session = requests.Session()
        session.headers.update({"User-Agent": "MigrasiLinux/1.0"})

        self.stdout.write("Mengambil daftar nama paket...")
        r = session.get(PACKAGES_GZ, timeout=60)
        r.raise_for_status()
        names = [ln.strip() for ln in gzip.decompress(r.content).decode().split("\n") if ln.strip()]
        self.stdout.write(f"Total {len(names)} paket AUR")

        inserted = updated = total = 0
        batches = [names[i:i + batch_size] for i in range(0, len(names), batch_size)]
        if max_batches:
            batches = batches[:max_batches]

        for n, batch in enumerate(batches, 1):
            results = []
            for attempt in range(1, 4):
                try:
                    resp = session.get(RPC_URL, params={"v": "5", "type": "info", "arg[]": batch}, timeout=60)
                    resp.raise_for_status()
                    data = resp.json()
                    if data.get("type") == "multiinfo":
                        results = data.get("results", [])
                    break
                except Exception as e:
                    self.stderr.write(f"batch {n} attempt {attempt} gagal: {e}")
                    time.sleep(2 * attempt)
            time.sleep(delay)

            if not results:
                continue
            ins, upd = self._bulk_upsert(results)
            inserted += ins
            updated += upd
            total += len(results)
            if n % 20 == 0:
                self.stdout.write(f"batch {n}/{len(batches)} total={total} ins={inserted} upd={updated}")

        log.total, log.inserted, log.updated = total, inserted, updated
        log.status = "done"
        log.finished_at = timezone.now()
        log.save()
        self.stdout.write(self.style.SUCCESS(f"selesai total={total} inserted={inserted} updated={updated}"))

    def _bulk_upsert(self, results):
        by_name = {p.get("Name", ""): p for p in results if p.get("Name")}
        existing = {o.name: o for o in RawPackage.objects.filter(source=Source.AUR, name__in=by_name)}
        to_create, to_update = [], []
        for name, p in by_name.items():
            extra = {
                "maintainer": p.get("Maintainer") or "",
                "votes": p.get("NumVotes", 0),
                "popularity": p.get("Popularity", 0),
                "first_submitted": p.get("FirstSubmitted", 0),
                "last_modified": p.get("LastModified", 0),
                "out_of_date": p.get("OutOfDate") or 0,
                "url": p.get("URL") or "",
                "license": p.get("License", []),
                "depends": p.get("Depends", []),
            }
            if name in existing:
                obj = existing[name]
                obj.version = p.get("Version", "")
                obj.description = p.get("Description") or ""
                obj.extra = extra
                to_update.append(obj)
            else:
                to_create.append(RawPackage(
                    source=Source.AUR, name=name,
                    version=p.get("Version", ""),
                    description=p.get("Description") or "",
                    extra=extra,
                ))
        ins = upd = 0
        if to_create:
            RawPackage.objects.bulk_create(to_create, batch_size=500)
            ins = len(to_create)
        if to_update:
            RawPackage.objects.bulk_update(to_update, ["version", "description", "extra"], batch_size=500)
            upd = len(to_update)
        return ins, upd
