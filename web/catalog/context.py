from django.db.models import Count, Q
from django.utils.translation import get_language
from .models import Category

DOCS = [
    ("install", "Install", "Install"),
    ("migrasi", "Migrasi", "Migration"),
    ("sumber-data", "Sumber Data", "Data Sources"),
    ("faq", "FAQ", "FAQ"),
    ("menjalankan", "Menjalankan Server", "Running the Server"),
    ("api", "API", "API"),
]


def sidebar(request):
    lang = "id" if get_language() == "id" else "en"
    cats = (Category.objects
            .annotate(n=Count("apps", filter=Q(apps__is_gui=True)))
            .filter(n__gt=0).order_by("-n"))
    return {"side_cats": cats, "side_docs": DOCS, "side_lang": lang}
