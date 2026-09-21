import time
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from catalog.models import RawPackage, Source, SyncLog


LIST_URL = "https://flathub.org/api/v2/appstream"
DETAIL_URL = "https://flathub.org/api/v2/appstream/{appid}"


class Command(BaseCommand):
    help = "Sync aplikasi Flathub ke RawPackage (daftar ID + detail per app, bulk upsert)"

    def add_arguments(self, parser):
        parser.add_argument("--max-apps", type=int, default=0)
        parser.add_argument("--delay", type=float, default=0.1)

    def fetch(self, session, url, retries=3):
        for attempt in range(1, retries + 1):
            try:
                r = session.get(url, timeout=30)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                if attempt == retries:
                    self.stderr.write(f"gagal {url}: {e}")
                    return None
                time.sleep(2 * attempt)
        return None

    def handle(self, *args, **opts):
        max_apps = opts["max_apps"] or None
        delay = opts["delay"]
        log = SyncLog.objects.create(source=Source.FLATHUB)
        session = requests.Session()
        session.headers.update({"User-Agent": "MigrasiLinux/1.0"})

        self.stdout.write("Mengambil daftar ID aplikasi...")
        appids = self.fetch(session, LIST_URL)
        if not appids:
            log.status = "failed"
            log.message = "gagal ambil daftar app"
            log.finished_at = timezone.now()
            log.save()
            return
        if max_apps:
            appids = appids[:max_apps]
        self.stdout.write(f"Total {len(appids)} aplikasi")

        metas = {}
        for i, appid in enumerate(appids, 1):
            meta = self.fetch(session, DETAIL_URL.format(appid=appid))
            if isinstance(meta, dict):
                metas[appid] = meta
            time.sleep(delay)
            if i % 200 == 0:
                self.stdout.write(f"  {i}/{len(appids)} detail terambil")

        existing = {o.name: o for o in RawPackage.objects.filter(source=Source.FLATHUB, name__in=metas)}
        to_create, to_update = [], []
        for appid, meta in metas.items():
            desc = meta.get("description") or ""
            extra = {
                "display_name": meta.get("name") or "",
                "summary": meta.get("summary") or "",
                "developer": meta.get("developer_name") or "",
                "categories": (meta.get("categories") or []) if isinstance(meta.get("categories"), list) else [],
                "homepage": meta.get("homepage") or meta.get("project_license") or "",
                "icon": meta.get("icon") or "",
            }
            if appid in existing:
                obj = existing[appid]
                obj.description = desc
                obj.extra = extra
                to_update.append(obj)
            else:
                to_create.append(RawPackage(
                    source=Source.FLATHUB, name=appid, description=desc,
                    architecture="flatpak", extra=extra,
                ))
        if to_create:
            RawPackage.objects.bulk_create(to_create, batch_size=500)
        if to_update:
            RawPackage.objects.bulk_update(to_update, ["description", "extra"], batch_size=500)

        log.total, log.inserted, log.updated = len(metas), len(to_create), len(to_update)
        log.status = "done"
        log.finished_at = timezone.now()
        log.save()
        self.stdout.write(self.style.SUCCESS(
            f"selesai total={len(metas)} inserted={len(to_create)} updated={len(to_update)}"))
