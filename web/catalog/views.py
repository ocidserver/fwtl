from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.utils.translation import get_language
from .models import Alternative, App, Category, RawPackage, WindowsApp


def _lang():
    return "id" if get_language() == "id" else "en"


def _cat_name(c, lang):
    return c.name_id if lang == "id" else c.name_en


def home(request):
    lang = _lang()
    q = request.GET.get("q", "").strip()
    results = []
    if q:
        results = (App.objects.filter(is_gui=True)
                   .filter(Q(display_name__icontains=q) | Q(slug__icontains=q))[:12])
    cats = Category.objects.annotate(n=Count("apps", filter=Q(apps__is_gui=True))).order_by("-n")
    wins = WindowsApp.objects.order_by("name")[:12]
    return render(request, "catalog/home.html", {
        "q": q, "results": results, "cats": cats, "wins": wins,
        "stats": {
            "apps": App.objects.filter(is_gui=True).count(),
            "wins": WindowsApp.objects.count(),
            "alts": Alternative.objects.count(),
        },
    })


def app_list(request):
    lang = _lang()
    q = request.GET.get("q", "").strip()
    cat_slug = request.GET.get("cat", "").strip()
    qs = App.objects.filter(is_gui=True).order_by("display_name")
    cat = None
    if cat_slug:
        cat = get_object_or_404(Category, slug=cat_slug)
        qs = qs.filter(categories=cat)
    if q:
        qs = qs.filter(Q(display_name__icontains=q) | Q(slug__icontains=q))
    qs = qs.prefetch_related("categories")
    page = Paginator(qs, 48).get_page(request.GET.get("page"))
    cats = Category.objects.order_by("name_id" if lang == "id" else "name_en")
    return render(request, "catalog/app_list.html",
                  {"page": page, "q": q, "cats": cats, "cat": cat})


def app_detail(request, slug):
    lang = _lang()
    app = get_object_or_404(App.objects.prefetch_related("categories", "packages"), slug=slug)
    pkgs = list(app.packages.all().order_by("source", "name"))
    alts = app.alternatives_for_windows.select_related("windows_app").order_by("-compatibility")
    info = {"cachyos": [], "aur": None, "flathub": None, "desc": "", "votes": 0,
            "popularity": 0.0, "downloads": 0, "maintainer": "", "licenses": [],
            "homepage": "", "icon": "", "developer": ""}
    for p in pkgs:
        ex = p.extra or {}
        if p.description and not info["desc"]:
            info["desc"] = p.description
        if p.source == "cachyos":
            info["cachyos"].append(p)
        elif p.source == "aur" and info["aur"] is None:
            info["aur"] = p
            info["votes"] = ex.get("votes", 0) or 0
            info["popularity"] = round(ex.get("popularity", 0) or 0, 2)
            info["maintainer"] = ex.get("maintainer", "")
            info["licenses"] = ex.get("license", []) or []
        elif p.source == "flathub" and info["flathub"] is None:
            info["flathub"] = p
            info["downloads"] = ex.get("downloads", 0) or 0
            info["homepage"] = ex.get("homepage", "")
            info["icon"] = ex.get("icon", "")
            info["developer"] = ex.get("display_name") and ex.get("developer", "") or ex.get("developer", "")
    return render(request, "catalog/app_detail.html",
                  {"app": app, "pkgs": pkgs, "alts": alts, **info})


def category_list(request):
    lang = _lang()
    cats = (Category.objects.annotate(n=Count("apps", filter=Q(apps__is_gui=True)))
            .order_by("-n"))
    return render(request, "catalog/category_list.html", {"cats": cats})


def category_detail(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    qs = App.objects.filter(is_gui=True, categories=cat).order_by("display_name")
    page = Paginator(qs, 48).get_page(request.GET.get("page"))
    wins = WindowsApp.objects.filter(category=cat).order_by("name")
    return render(request, "catalog/category_detail.html",
                  {"cat": cat, "page": page, "wins": wins})


def windows_list(request):
    q = request.GET.get("q", "").strip()
    qs = WindowsApp.objects.order_by("name")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(slug__icontains=q))
    qs = qs.annotate(n=Count("alternatives")).select_related("category")
    page = Paginator(qs, 48).get_page(request.GET.get("page"))
    return render(request, "catalog/windows_list.html", {"page": page, "q": q})


def windows_detail(request, slug):
    lang = _lang()
    win = get_object_or_404(WindowsApp.objects.select_related("category"), slug=slug)
    alts = (win.alternatives.select_related("app")
            .prefetch_related("app__categories", "app__packages")
            .order_by("-compatibility"))
    return render(request, "catalog/windows_detail.html", {"win": win, "alts": alts})


def top_list(request):
    votes = (RawPackage.objects.filter(source="aur", extra__votes__gt=0)
             .select_related("app").order_by("-extra__votes")[:20])
    pop = (RawPackage.objects.filter(source="aur", extra__popularity__gt=0)
           .select_related("app").order_by("-extra__popularity")[:20])
    dls = (RawPackage.objects.filter(source="flathub", extra__downloads__gt=0)
           .select_related("app").order_by("-extra__downloads")[:20])
    replaced = (App.objects.filter(is_gui=True)
                .annotate(n=Count("alternatives_for_windows"))
                .filter(n__gt=0).order_by("-n")[:20])
    return render(request, "catalog/top_list.html",
                  {"votes": votes, "pop": pop, "dls": dls, "replaced": replaced})


DOC_PAGES = ["install", "migrasi", "sumber-data", "faq"]


def doc_page(request, slug):
    if slug not in DOC_PAGES:
        from django.http import Http404
        raise Http404
    return render(request, f"catalog/docs/{slug}.html", {"doc_slug": slug})
