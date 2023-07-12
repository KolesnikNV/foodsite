from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagsViewSet

app_name = "food"

router = DefaultRouter()

router.register(r"tags", TagsViewSet, basename="tags")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("", include(router.urls)),
]
