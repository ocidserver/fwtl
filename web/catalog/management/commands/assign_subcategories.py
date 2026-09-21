import re
from collections import defaultdict
from django.core.management.base import BaseCommand
from catalog.models import App, SubCategory

STRIP_SUFFIX = re.compile(r"-(bin|git|svn|hg|bzr|appimage|flatpak|nightly|beta|stable|lts)$")


def compile_matcher(kws):
    """Keyword pendek (<=3) pakai word-boundary agar 'tar' tak cocok 'avatar'."""
    subs, res = [], []
    for k in kws:
        if len(k) <= 3:
            res.append(re.compile(r"\b" + re.escape(k) + r"\b"))
        else:
            subs.append(k)
    def match(text):
        if any(k in text for k in subs):
            return True
        return any(r.search(text) for r in res)
    return match


class Command(BaseCommand):
    help = "Assign App GUI ke subkategori via keyword dalam induk kategorinya"

    def handle(self, *args, **opts):
        subs = list(SubCategory.objects.select_related("category").order_by("priority"))
        by_cat = defaultdict(list)
        for s in subs:
            kws = [k.strip().lower() for k in (s.keywords or "").split(",") if k.strip()]
            by_cat[s.category_id].append((s, compile_matcher(kws)))
        other_by_cat = {s.category_id: s for s in subs if s.slug.endswith("--other")}

        Through = App.subcategories.through
        Through.objects.all().delete()
        m2m, done = [], 0
        qs = (App.objects.filter(is_gui=True).prefetch_related("categories", "packages")
              .only("id", "slug", "display_name"))
        total = qs.count()
        for app in qs.iterator(chunk_size=5000):
            cat_ids = [c.id for c in app.categories.all()]
            names = {STRIP_SUFFIX.sub('', app.slug), STRIP_SUFFIX.sub('', app.display_name.lower())}
            descs = []
            for p in app.packages.all():
                base = STRIP_SUFFIX.sub("", (p.name or "").lower())
                names.add(base)
                if p.description:
                    descs.append(p.description[:300].lower())
            text = f"{' '.join(names)} {' '.join(descs[:3])}"
            for cid in cat_ids:
                matched = None
                for sub, is_match in by_cat.get(cid, []):
                    if is_match(text):
                        matched = sub
                        break
                if matched is None:
                    matched = other_by_cat.get(cid)
                if matched:
                    m2m.append(Through(app_id=app.id, subcategory_id=matched.id))
            done += 1
            if done % 20000 == 0:
                self.stdout.write(f"  {done}/{total}")
            if len(m2m) >= 10000:
                Through.objects.bulk_create(m2m, batch_size=2000, ignore_conflicts=True)
                m2m = []
        if m2m:
            Through.objects.bulk_create(m2m, batch_size=2000, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(
            f"selesai: {Through.objects.count()} relasi app-subkategori"))
