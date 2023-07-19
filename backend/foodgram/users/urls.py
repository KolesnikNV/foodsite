from django.urls import include, path
from djoser.views import TokenCreateView
from rest_framework.routers import DefaultRouter

from .views import CustomTokenDestroyView, SubscriptionListView, follow_author

app_name = "users"

api_router_v1 = DefaultRouter()
api_router_v1.register(
    r"users/subscriptions",
    SubscriptionListView,
    basename="subscriptions",
)


urlpatterns = [
    path(r"", include(api_router_v1.urls)),
    path(r"auth/token/login/", TokenCreateView.as_view(), name="token_create"),
    path(r"users/<int:pk>/subscribe/", follow_author, name="follow-author"),
    path(
        r"auth/token/logout/", CustomTokenDestroyView.as_view(), name="logout"
    ),
    path(r"", include("djoser.urls")),
]
