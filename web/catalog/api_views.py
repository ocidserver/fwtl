"""Read-only JSON API (tanpa DRF). Semua GET, paginasi ?page=."""
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from .models import Alternative, App, Category, WindowsApp

PER_PAGE = 50


def _page(qs, request):
    p = Paginator(qs, PER_PAGE).get_page(request.GET.get("page"))
    return p, {"page": p.number, "pages": p.paginator.num_pages, "total": p.paginator.count}


def _app_json(a, lang="id"):
    pkgs = [{"source": p.source, "name": p.name, "version": p.version,
             "repository": p.repository} for p in a.packages.all()]
    aur = next((p for p in a.packages.all() if p.source == "aur"), None)
    flat = next((p for p in a.packages.all() if p.source == "flathub"), None)
    ex_a = (aur.extra or {}) if aur else {}
    ex_f = (flat.extra or {}) if flat else {}
    return {
        "slug": a.slug, "name": a.display_name, "is_gui": a.is_gui,
        "categories": [c.slug for c in a.categories.all()],
        "votes": (ex_a.get("votes") or 0), "popularity": round(ex_a.get("popularity") or 0, 2),
        "downloads": ex_f.get("downloads") or 0,
        "maintainer": ex_a.get("maintainer") or "",
        "install": {
            "cachyos": next((f"sudo pacman -S {p.name}" for p in a.packages.all()
                             if p.source == "cachyos"), ""),
            "aur": f"yay -S {aur.name}" if aur else "",
            "flathub": f"flatpak install flathub {flat.name}" if flat else "",
        },
        "packages": pkgs,
    }


@require_GET
@cache_control(max_age=300, s_maxage=3600)
def api_apps(request):
    q = request.GET.get("q", "").strip()
    qs = App.objects.filter(is_gui=True).order_by("display_name").prefetch_related("categories", "packages")
    if q:
        qs = qs.filter(Q(display_name__icontains=q) | Q(slug__icontains=q))
    if request.GET.get("cat"):
        qs = qs.filter(categories__slug=request.GET["cat"])
    page, meta = _page(qs, request)
    return JsonResponse({"meta": meta, "results": [_app_json(a) for a in page]})


@require_GET
@cache_control(max_age=300, s_maxage=3600)
def api_app_detail(request, slug):
    a = get_object_or_404(App.objects.prefetch_related("categories", "packages"), slug=slug)
    d = _app_json(a)
    d["alternatives_for_windows"] = [
        {"windows_app": alt.windows_app.name, "compatibility": alt.compatibility}
        for alt in a.alternatives_for_windows.filter(is_published=True)]
    return JsonResponse(d)


@require_GET
@cache_control(max_age=300, s_maxage=3600)
def api_categories(request):
    cats = Category.objects.annotate(n=Count("apps", filter=Q(apps__is_gui=True))).order_by("-n")
    return JsonResponse({"results": [
        {"slug": c.slug, "name_id": c.name_id, "name_en": c.name_en, "apps": c.n,
         "subs": [{"slug": s.slug.split("--")[-1], "name_id": s.name_id, "name_en": s.name_en}
                  for s in c.subs.all()]} for c in cats]})


@require_GET
@cache_control(max_age=300, s_maxage=3600)
def api_windows(request):
    q = request.GET.get("q", "").strip()
    qs = WindowsApp.objects.order_by("name")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(slug__icontains=q))
    page, meta = _page(qs, request)
    out = []
    for w in page:
        alts = w.alternatives.filter(is_published=True).select_related("app").order_by("-compatibility")
        out.append({"slug": w.slug, "name": w.name,
                    "alternatives": [{"app": a.app.slug, "name": a.app.display_name,
                                      "compatibility": a.compatibility,
                                      "notes_id": a.notes_id, "notes_en": a.notes_en,
                                      "install_cachyos": a.install_cachyos,
                                      "install_aur": a.install_aur,
                                      "install_flathub": a.install_flathub} for a in alts]})
    return JsonResponse({"meta": meta, "results": out})


@require_GET
@cache_control(max_age=300, s_maxage=3600)
def api_top(request):
    from .models import RawPackage
    top_v = [{"app": (p.app.slug if p.app else None), "name": (p.app.display_name if p.app else p.name),
              "votes": (p.extra or {}).get("votes", 0)}
             for p in RawPackage.objects.filter(source="aur", extra__votes__gt=0)
             .select_related("app").order_by("-extra__votes")[:20]]
    top_d = [{"app": (p.app.slug if p.app else None), "name": (p.app.display_name if p.app else p.name),
              "downloads": (p.extra or {}).get("downloads", 0)}
             for p in RawPackage.objects.filter(source="flathub", extra__downloads__gt=0)
             .select_related("app").order_by("-extra__downloads")[:20]]
    return JsonResponse({"by_votes": top_v, "by_downloads": top_d})
