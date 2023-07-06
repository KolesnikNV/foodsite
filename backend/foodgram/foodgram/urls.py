from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from djoser.views import TokenCreateView
from food.views import TagsViewSet, IngredientViewSet, RecipeViewSet


router = routers.DefaultRouter()
router.register(r"tags", TagsViewSet)
router.register(r"ingredients", IngredientViewSet)
router.register(r"recipes", RecipeViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/", include("djoser.urls")),
    path("api/", include("djoser.urls.authtoken")),
    path("auth/token/login/", TokenCreateView.as_view(), name="login"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
