from django.contrib import admin
from .models import (Alternative, App, Category, CategoryRule, RawPackage,
                     SubCategory, SyncLog, WindowsApp)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("slug", "name_id", "name_en")
    search_fields = ("slug", "name_id", "name_en")


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("slug", "name_id", "category", "priority")
    list_filter = ("category",)
    search_fields = ("slug", "name_id", "name_en", "keywords")


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ("display_name", "slug", "is_gui")
    list_filter = ("is_gui", "categories")
    search_fields = ("display_name", "slug")
    filter_horizontal = ("categories", "subcategories")
    actions = ["tandai_gui", "tandai_non_gui"]

    @admin.action(description="Tandai sebagai GUI")
    def tandai_gui(self, request, qs):
        qs.update(is_gui=True)

    @admin.action(description="Tandai sebagai non-GUI")
    def tandai_non_gui(self, request, qs):
        qs.update(is_gui=False)


@admin.register(CategoryRule)
class CategoryRuleAdmin(admin.ModelAdmin):
    list_display = ("keyword", "category", "priority")
    list_filter = ("category",)
    search_fields = ("keyword",)


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
    list_display = ("windows_app", "app", "compatibility", "is_published")
    list_filter = ("is_published", "compatibility")
    search_fields = ("windows_app__name", "app__display_name")
    actions = ["publish", "unpublish"]

    @admin.action(description="Publish terpilih")
    def publish(self, request, qs):
        qs.update(is_published=True)

    @admin.action(description="Unpublish terpilih")
    def unpublish(self, request, qs):
        qs.update(is_published=False)


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ("source", "started_at", "status", "total", "inserted", "updated")
    list_filter = ("source", "status")
