import re
from collections import defaultdict
from django.core.management.base import BaseCommand
from catalog.models import App, Category, CategoryRule

CORE_REPOS = {"core", "cachyos-core-v3", "cachyos-core-v4"}
STRIP_SUFFIX = re.compile(r"-(bin|git|svn|hg|bzr|appimage|flatpak|nightly|beta|stable|lts)$")


def compile_matcher(kws):
    """Keyword pendek (<=3) hanya cocok di NAMA (presisi); panjang di nama+deskripsi."""
    subs = [k for k in kws if len(k) > 3]
    res = [re.compile(r"\b" + re.escape(k) + r"\b") for k in kws if len(k) <= 3]
    def match(names_text, full_text):
        if any(k in full_text for k in subs):
            return True
        return any(r.search(names_text) for r in res)
    return match


EXTRA_RULES = {
    "development-tools": ["lazygit", "golang", "gitkraken", "git-cola", "gitui", "gitahead", "tig"],
    "text-editor-ide": ["neovim", "kakoune"],
}


class Command(BaseCommand):
    help = "Hitung ulang App.categories dengan word-boundary untuk keyword pendek"

    def handle(self, *args, **opts):
        from catalog.models import CategoryRule as CR
        for cslug, kws in EXTRA_RULES.items():
            try:
                cat = Category.objects.get(slug=cslug)
                for k in kws:
                    CR.objects.get_or_create(category=cat, keyword=k)
            except Category.DoesNotExist:
                pass
        rules, cat_by_slug = defaultdict(list), {}
        for cr in CategoryRule.objects.select_related("category"):
            rules[cr.category.slug].append(cr.keyword.lower())
            cat_by_slug[cr.category.slug] = cr.category.id
        matchers = {s: compile_matcher(kws) for s, kws in rules.items()}
        lib_id = cat_by_slug.get("libraries-dependencies")
        sys_id = cat_by_slug.get("system-utilities")
        other_id = cat_by_slug.get("other")

        Through = App.categories.through
        Through.objects.all().delete()
        m2m, done = [], 0
        total = App.objects.count()
        qs = App.objects.prefetch_related("categories", "packages").only("id", "slug", "display_name")
        for app in qs.iterator(chunk_size=5000):
            names = {STRIP_SUFFIX.sub("", app.slug),
                     STRIP_SUFFIX.sub("", (app.display_name or "").lower())}
            descs, repos = [], set()
            for p in app.packages.all():
                names.add(STRIP_SUFFIX.sub("", (p.name or "").lower()))
                if p.description:
                    descs.append(p.description[:400].lower())
                if p.repository:
                    repos.add(p.repository)
            text = f"{' '.join(names)} {' '.join(descs[:3])}"
            names_text = " ".join(names)
            matched = {s for s, m in matchers.items() if m(names_text, text)}
            if not matched:
                if "lib" in app.slug or "library" in text:
                    matched = {"libraries-dependencies"}
                elif repos and repos <= CORE_REPOS:
                    matched = {"system-utilities"}
                else:
                    matched = {"other"}
            for s in matched:
                if s in cat_by_slug:
                    m2m.append(Through(app_id=app.id, category_id=cat_by_slug[s]))
            done += 1
            if done % 20000 == 0:
                self.stdout.write(f"  {done}/{total}")
            if len(m2m) >= 10000:
                Through.objects.bulk_create(m2m, batch_size=2000, ignore_conflicts=True)
                m2m = []
        if m2m:
            Through.objects.bulk_create(m2m, batch_size=2000, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(
            f"selesai: {Through.objects.count()} relasi app-kategori"))
