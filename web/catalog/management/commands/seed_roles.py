from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from catalog.models import Alternative, App, Category, SubCategory, WindowsApp


class Command(BaseCommand):
    help = "Buat grup Editor (kelola konten katalog, tanpa kelola user)"

    def handle(self, *args, **opts):
        group, _ = Group.objects.get_or_create(name="Editor")
        ct = ContentType.objects.get_for_models(App, Category, SubCategory, WindowsApp, Alternative)
        perms = Permission.objects.filter(
            content_type__in=ct.values(),
            codename__regex=r"^(view|change)_")
        group.permissions.set(perms)
        self.stdout.write(self.style.SUCCESS(
            f"grup Editor: {group.permissions.count()} permissions"))
