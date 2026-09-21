from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.utils.translation import get_language
from .models import Alternative, App, Category, WindowsApp


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
    pkgs = app.packages.all().order_by("source", "name")
    alts = app.alternatives_for_windows.select_related("windows_app").order_by("-compatibility")
    desc = ""
    for p in pkgs:
        if p.description:
            desc = p.description
            break
    return render(request, "catalog/app_detail.html",
                  {"app": app, "pkgs": pkgs, "alts": alts, "desc": desc})


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
