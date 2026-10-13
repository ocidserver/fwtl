from django.urls import path
from catalog import api_views

urlpatterns = [
    path("api/apps/", api_views.api_apps, name="api-apps"),
    path("api/apps/<slug:slug>/", api_views.api_app_detail, name="api-app-detail"),
    path("api/categories/", api_views.api_categories, name="api-categories"),
    path("api/windows/", api_views.api_windows, name="api-windows"),
    path("api/top/", api_views.api_top, name="api-top"),
]
