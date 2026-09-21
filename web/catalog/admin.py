from django.contrib import admin
from .models import App, Alternative, Category, CategoryRule, RawPackage, SyncLog, WindowsApp


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("slug", "name_id", "name_en")
    search_fields = ("slug", "name_id", "name_en")


@admin.register(CategoryRule)
class CategoryRuleAdmin(admin.ModelAdmin):
    list_display = ("keyword", "category", "priority")
    list_filter = ("category",)
    search_fields = ("keyword",)


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ("display_name", "slug", "is_gui")
    list_filter = ("is_gui", "categories")
    search_fields = ("display_name", "slug")
    filter_horizontal = ("categories",)


@admin.register(RawPackage)
class RawPackageAdmin(admin.ModelAdmin):
    list_display = ("source", "name", "version", "repository", "app")
    list_filter = ("source", "repository")
    search_fields = ("name",)


@admin.register(WindowsApp)
class WindowsAppAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor", "category")
    search_fields = ("name",)


@admin.register(Alternative)
class AlternativeAdmin(admin.ModelAdmin):
    list_display = ("windows_app", "app", "compatibility")
    list_filter = ("compatibility",)


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ("source", "started_at", "status", "total", "inserted", "updated")
    list_filter = ("source", "status")
