from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

api_patterns = [
    path("", include("users.urls", namespace="api_users")),
    path("", include("food.urls", namespace="api_food")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_patterns)),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
