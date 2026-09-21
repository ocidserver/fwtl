import time
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from catalog.models import RawPackage, Source, SyncLog


API_URL = "https://packages.cachyos.org/api/search"


class Command(BaseCommand):
    help = "Sync paket CachyOS ke RawPackage (incremental sederhana + retry)"

    def add_arguments(self, parser):
        parser.add_argument("--max-pages", type=int, default=0)
        parser.add_argument("--page-size", type=int, default=100)
        parser.add_argument("--delay", type=float, default=0.2)

    def fetch_page(self, session, page, page_size, retries=3):
        for attempt in range(1, retries + 1):
            try:
                r = session.get(API_URL, params={"current_page": page, "page_size": page_size}, timeout=30)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                self.stderr.write(f"page {page} attempt {attempt} gagal: {e}")
                time.sleep(1.5 * attempt)
        return {}

    def handle(self, *args, **opts):
        max_pages = opts["max_pages"] or None
        page_size = opts["page_size"]
        delay = opts["delay"]
        log = SyncLog.objects.create(source=Source.CACHYOS)
        session = requests.Session()
        session.headers.update({"User-Agent": "MigrasiLinux/1.0"})

        data = self.fetch_page(session, 1, page_size)
        if not data:
            log.status = "failed"
            log.message = "gagal ambil halaman 1"
            log.finished_at = timezone.now()
            log.save()
            return

        total_pages = data.get("total_pages", 0)
        if max_pages:
            total_pages = min(total_pages, max_pages)
        self.stdout.write(f"total_pages={total_pages} page_size={page_size}")

        inserted = updated = total = 0
        pages = [data]
        for p in range(2, total_pages + 1):
            time.sleep(delay)
            pages.append(self.fetch_page(session, p, page_size))

        for page_data in pages:
            for pkg in page_data.get("packages", []):
                total += 1
                name = pkg.get("pkg_name", "")
                repo = pkg.get("repo_name", "")
                arch = pkg.get("pkg_arch", "")
                if not name:
                    continue
                obj, created = RawPackage.objects.update_or_create(
                    source=Source.CACHYOS, name=name, repository=repo, architecture=arch,
                    defaults={
                        "version": pkg.get("pkg_version", ""),
                        "description": pkg.get("pkg_desc", ""),
                        "extra": {
                            "build_date_unix": pkg.get("pkg_builddate", 0),
                            "installed_size": pkg.get("pkg_isize", ""),
                            "compressed_size": pkg.get("pkg_csize", ""),
                        },
                    },
                )
                if created:
                    inserted += 1
                else:
                    updated += 1

        log.total, log.inserted, log.updated = total, inserted, updated
        log.status = "done"
        log.finished_at = timezone.now()
        log.save()
        self.stdout.write(self.style.SUCCESS(f"selesai total={total} inserted={inserted} updated={updated}"))
