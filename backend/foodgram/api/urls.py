from api.views import (CustomTokenDestroyView, FollowAuthorView,
                       IngredientViewSet, RecipeViewSet, SubscriptionListView,
                       TagsViewSet)
from django.urls import include, path
from djoser.views import TokenCreateView
from rest_framework.routers import DefaultRouter

app_name = "api"

router = DefaultRouter()

router.register(r"tags", TagsViewSet, basename="tags")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")
router.register(
    r"users/subscriptions",
    SubscriptionListView,
    basename="subscriptions",
)
router.register(
    "users/<int:pk>/subscribe/",
    FollowAuthorView,
    basename="follow-author",
)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/login/", TokenCreateView.as_view(), name="token_create"),
    path(
        "auth/token/logout/", CustomTokenDestroyView.as_view(), name="logout"
    ),
    path("", include("djoser.urls")),
]
