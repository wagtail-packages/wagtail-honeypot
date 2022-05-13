from django.contrib import admin
from django.urls import include, path
from wagtail.admin import urls as wagtailadmin_urls

try:
    from wagtail import urls as wagtail_urls
except ImportError:
    from wagtail.core import urls as wagtail_urls

from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("", include(wagtail_urls)),
]
