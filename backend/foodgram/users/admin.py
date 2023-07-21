from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Административный класс для модели User.
    """

    list_display = (
        "pk",
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
    )
    list_filter = ("email", "username")
    search_fields = ("username",)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """
    Административный класс для модели Follow.
    """

    list_display = ("pk", "user", "author")
    list_filter = ("user", "author")
    search_fields = ("author",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "author")
