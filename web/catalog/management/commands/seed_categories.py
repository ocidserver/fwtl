import sys
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Category, CategoryRule

# package_classifier.py ada di root repo (satu level di atas web/)
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from package_classifier import PackageClassifier  # noqa: E402

# Terjemahan ID untuk nama kategori (fallback: pakai nama EN)
NAME_ID = {
    "Web Browser": "Peramban Web",
    "Office & Productivity": "Perkantoran & Produktivitas",
    "Media Player & Video": "Pemutar Media & Video",
    "Audio & Music": "Audio & Musik",
    "Graphics & Image Editing": "Grafis & Olah Gambar",
    "Video Editing": "Olah Video",
    "Development Tools": "Perkakas Pengembangan",
    "Text Editor & IDE": "Editor Teks & IDE",
    "Gaming": "Gim",
    "Email Client": "Klien Surel",
    "File Manager": "Manajer Berkas",
    "Archive & Compression": "Arsip & Kompresi",
    "Download Manager": "Manajer Unduhan",
    "Remote Desktop & VNC": "Desktop Jauh & VNC",
    "Communication & Chat": "Komunikasi & Obrolan",
    "Security & Privacy": "Keamanan & Privasi",
    "System Utilities": "Utilitas Sistem",
    "Database": "Basis Data",
    "Virtualization": "Virtualisasi",
    "Terminal & Shell": "Terminal & Shell",
    "Desktop Environment": "Lingkungan Desktop",
    "Libraries & Dependencies": "Pustaka & Dependensi",
    "Networking": "Jaringan",
    "Web Development": "Pengembangan Web",
    "Cloud & Sync": "Awan & Sinkronisasi",
    "CAD & 3D Modeling": "CAD & Model 3D",
    "Scientific & Math": "Sains & Matematika",
    "Fonts & Typography": "Fonta & Tipografi",
    "Printing & Scanning": "Cetak & Pindai",
}


class Command(BaseCommand):
    help = "Seed 29 kategori + rules keyword dari package_classifier.py"

    def handle(self, *args, **opts):
        clf = PackageClassifier()
        n_cat = n_rule = 0
        for name_en, info in clf.categories.items():
            cat, created = Category.objects.get_or_create(
                slug=slugify(name_en),
                defaults={"name_id": NAME_ID.get(name_en, name_en), "name_en": name_en},
            )
            if created:
                n_cat += 1
            for kw in info.get("keywords", []):
                _, rc = CategoryRule.objects.get_or_create(category=cat, keyword=kw.lower())
                if rc:
                    n_rule += 1
        # kategori penampung "Other"
        Category.objects.get_or_create(slug="other", defaults={"name_id": "Lainnya", "name_en": "Other"})
        self.stdout.write(self.style.SUCCESS(
            f"selesai: {Category.objects.count()} kategori, {CategoryRule.objects.count()} rules "
            f"(baru: {n_cat} kat, {n_rule} rule)"))
