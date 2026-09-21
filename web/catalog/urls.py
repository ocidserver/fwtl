from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("apps/", views.app_list, name="app-list"),
    path("app/<slug:slug>/", views.app_detail, name="app-detail"),
    path("kategori/", views.category_list, name="category-list"),
    path("kategori/<slug:slug>/", views.category_detail, name="category-detail"),
    path("windows/", views.windows_list, name="windows-list"),
    path("windows/<slug:slug>/", views.windows_detail, name="windows-detail"),
    path("top/", views.top_list, name="top-list"),
    path("docs/<slug:slug>/", views.doc_page, name="doc-page"),
]
