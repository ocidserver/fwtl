from django.db import models
from django.utils.text import slugify


class Source(models.TextChoices):
    CACHYOS = "cachyos", "CachyOS"
    AUR = "aur", "AUR"
    FLATHUB = "flathub", "Flathub"


class Category(models.Model):
    slug = models.SlugField(max_length=80, unique=True)
    name_id = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120)
    description_id = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    class Meta:
        ordering = ["name_id"]

    def __str__(self):
        return self.name_id

    def save(self, *args, **kwargs):
        if not self.slug and self.name_en:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)


class CategoryRule(models.Model):
    """Aturan keyword (port dari package_classifier.py) + allowlist manual."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="rules")
    keyword = models.CharField(max_length=120)
    priority = models.IntegerField(default=0)

    class Meta:
        ordering = ["-priority", "keyword"]

    def __str__(self):
        return f"{self.keyword} -> {self.category.slug}"


class App(models.Model):
    """Entitas kanonis: gabungan nama yang sama lintas sumber."""
    slug = models.SlugField(max_length=120, unique=True)
    display_name = models.CharField(max_length=200)
    summary_id = models.CharField(max_length=300, blank=True)
    summary_en = models.CharField(max_length=300, blank=True)
    description_id = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    categories = models.ManyToManyField(Category, blank=True, related_name="apps")
    is_gui = models.BooleanField(default=True)
    homepage = models.URLField(blank=True)
    icon_url = models.URLField(blank=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self):
        return self.display_name


class RawPackage(models.Model):
    """Snapshot mentah per sumber — hasil sync ETL."""
    source = models.CharField(max_length=20, choices=Source.choices, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    version = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    repository = models.CharField(max_length=120, blank=True)
    architecture = models.CharField(max_length=40, blank=True)
    extra = models.JSONField(default=dict, blank=True)  # votes, popularity, flatpak id, dsb
    app = models.ForeignKey(App, null=True, blank=True, on_delete=models.SET_NULL, related_name="packages")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("source", "name", "repository", "architecture")]
        indexes = [models.Index(fields=["source", "name"])]

    def __str__(self):
        return f"[{self.source}] {self.name}"


class WindowsApp(models.Model):
    slug = models.SlugField(max_length=120, unique=True)
    name = models.CharField(max_length=200, unique=True)
    vendor = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Alternative(models.Model):
    windows_app = models.ForeignKey(WindowsApp, on_delete=models.CASCADE, related_name="alternatives")
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name="alternatives_for_windows")
    compatibility = models.PositiveSmallIntegerField(default=80, help_text="0-100")
    notes_id = models.TextField(blank=True)
    notes_en = models.TextField(blank=True)
    install_cachyos = models.CharField(max_length=200, blank=True)
    install_aur = models.CharField(max_length=200, blank=True)
    install_flathub = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = [("windows_app", "app")]

    def __str__(self):
        return f"{self.windows_app} -> {self.app} ({self.compatibility}%)"


class SyncLog(models.Model):
    source = models.CharField(max_length=20, choices=Source.choices)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    total = models.IntegerField(default=0)
    inserted = models.IntegerField(default=0)
    updated = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="running")
    message = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.source} {self.started_at:%Y-%m-%d %H:%M} {self.status}"
