import re
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils.text import slugify
from catalog.models import App, Category, CategoryRule, RawPackage, Source


STRIP_SUFFIX = re.compile(r"-(bin|git|svn|hg|bzr|appimage|flatpak|nightly|beta|stable|lts)$")
LIB_PREFIX = re.compile(
    r"^(lib|lib32|python-|perl-|haskell-|ruby-|php-|lua|luajit|texlive-|ttf-|otf-|"
    r"xf86-|gcc|glibc|gstreamer|gst-|mesa-|nvidia-|amd-|intel-|firmware-|dkms)"
)
DEV_SUFFIX = re.compile(r"-(dev|devel|headers|debug|dbg|doc|docs|common-data)$")


def base_key(name: str, source: str) -> str:
    n = (name or "").strip().lower()
    if source == Source.FLATHUB and "." in n:
        n = n.rsplit(".", 1)[-1]  # org.mozilla.firefox -> firefox
    n = STRIP_SUFFIX.sub("", n)
    return n or name.lower()


def gui_flag(key: str, cats: set) -> bool:
    if LIB_PREFIX.match(key) or DEV_SUFFIX.search(key):
        return False
    if cats in ({"libraries-dependencies"}, {"fonts-typography"}):
        return False
    return True


class Command(BaseCommand):
    help = "Bangun App kanonis lintas sumber + klasifikasi kategori + tandai is_gui"

    def add_arguments(self, parser):
        parser.add_argument("--link-only", action="store_true",
                            help="Hanya tautkan RawPackage yang app-nya NULL (resume, aman diulang)")
        parser.add_argument("--batch-size", type=int, default=2000)

    def handle(self, *args, **opts):
        rules = defaultdict(list)
        for cr in CategoryRule.objects.select_related("category"):
            rules[cr.category.slug].append(cr.keyword)
        # Semua kategori agar fallback 'other' tak terbuang
        cat_by_slug = {c.slug: c.id for c in Category.objects.all()}
        self.stdout.write(f"rules: {sum(len(v) for v in rules.values())} keyword / {len(rules)} kategori")

        self.stdout.write("Memuat RawPackage...")
        groups, count = {}, 0
        for rp in RawPackage.objects.only("id", "source", "name", "description", "repository", "extra").iterator(chunk_size=5000):
            count += 1
            key = base_key(rp.name, rp.source)
            g = groups.get(key)
            if g is None:
                g = groups[key] = {"best": rp.name, "score": -1, "flat": "",
                                   "names": set(), "descs": [], "ids": [], "repos": set()}
            votes = 0
            if isinstance(rp.extra, dict):
                votes = rp.extra.get("votes", 0) or 0
                if rp.source == Source.FLATHUB and rp.extra.get("display_name"):
                    g["flat"] = rp.extra["display_name"]
            score = {"flathub": 3_000_000, "cachyos": 2_000_000, "aur": 0}[rp.source] + min(votes, 999_999)
            if score > g["score"]:
                g["score"], g["best"] = score, rp.name
            g["names"].add(rp.name)
            if rp.description:
                g["descs"].append(rp.description[:400])
            g["ids"].append(rp.id)
            if rp.repository:
                g["repos"].add(rp.repository)
            if count % 50000 == 0:
                self.stdout.write(f"  {count} raw, {len(groups)} grup")
        self.stdout.write(f"total {count} raw -> {len(groups)} grup kanonis")

        # Link-only: tiru kondisi build awal (used kosong) agar mapping slug identik.
        # Jika di-seed dari DB, semua slug dianggap tabrakan dan mapping bergeser total.
        used_slugs = set() if opts["link_only"] else set(App.objects.values_list("slug", flat=True))
        to_create, key2slug, key2cats = [], {}, {}
        for key, g in groups.items():
            text = f"{key} {' '.join(g['names'])} {' '.join(g['descs'][:3])}".lower()
            matched = {s for s, kws in rules.items() if any(k in text for k in kws)}
            if not matched:
                if "lib" in key or "library" in text:
                    matched = {"libraries-dependencies"}
                elif g["repos"] and g["repos"] <= {"core", "cachyos-core-v3", "cachyos-core-v4"}:
                    matched = {"system-utilities"}
                else:
                    matched = {"other"}
            slug = slugify(key)[:110] or f"app-{len(used_slugs)}"
            i = 1
            base = slug
            while slug in used_slugs:
                i += 1
                slug = f"{base}-{i}"[:120]
            used_slugs.add(slug)
            if not opts["link_only"]:
                disp = (g["flat"] or g["best"])[:200]
                to_create.append(App(slug=slug, display_name=disp, is_gui=gui_flag(key, matched)))
            key2slug[key] = slug
            key2cats[key] = matched

        if opts["link_only"]:
            id_by_slug = dict(App.objects.values_list("slug", "id"))
            null_ids = set(RawPackage.objects.filter(app__isnull=True).values_list("id", flat=True))
            self.stdout.write(f"resume: {len(null_ids)} RawPackage belum tertaut")
            batch, done = [], 0
            bs = opts["batch_size"]
            for key, g in groups.items():
                aid = id_by_slug.get(key2slug[key])
                if aid is None:
                    continue
                for rid in g["ids"]:
                    if rid not in null_ids:
                        continue
                    batch.append((aid, rid))
                    if len(batch) >= bs:
                        self._flush(batch)
                        done += len(batch)
                        batch = []
                        if done % 20000 < bs:
                            self.stdout.write(f"  {done} tertaut...")
            if batch:
                self._flush(batch)
                done += len(batch)
            left = RawPackage.objects.filter(app__isnull=True).count()
            self.stdout.write(self.style.SUCCESS(f"selesai link-only: {done} ditautkan, sisa NULL: {left}"))
            return

        App.objects.bulk_create(to_create, batch_size=1000)
        self.stdout.write(f"{len(to_create)} App dibuat")
        id_by_slug = dict(App.objects.values_list("slug", "id"))

        Through = App.categories.through
        m2m = [Through(app_id=id_by_slug[s], category_id=cat_by_slug[c])
               for key, s in key2slug.items() for c in key2cats[key] if c in cat_by_slug]
        Through.objects.bulk_create(m2m, batch_size=2000, ignore_conflicts=True)
        self.stdout.write(f"{len(m2m)} relasi app-kategori")

        self.stdout.write("Menautkan RawPackage -> App...")
        batch, done = [], 0
        for key, g in groups.items():
            aid = id_by_slug.get(key2slug[key])
            for rid in g["ids"]:
                batch.append((aid, rid))
                if len(batch) >= 5000:
                    self._flush(batch)
                    done += len(batch)
                    batch = []
        if batch:
            self._flush(batch)
            done += len(batch)
        self.stdout.write(self.style.SUCCESS(f"selesai: {len(groups)} App, {done} RawPackage tertaut"))

    def _flush(self, batch):
        with connection.cursor() as c:
            c.executemany("UPDATE catalog_rawpackage SET app_id=%s WHERE id=%s", batch)
