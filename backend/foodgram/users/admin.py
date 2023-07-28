from admin_auto_filters.filters import AutocompleteFilter

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
    search_fields = ("username",)


class UserAutocompleteFilter(AutocompleteFilter):
    title = "User"
    field_name = "user"


class AuthorAutocompleteFilter(AutocompleteFilter):
    title = "Author"
    field_name = "author"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """
    Административный класс для модели Follow.
    """

    list_display = ("pk", "user", "author")
    list_filter = (
        UserAutocompleteFilter,
        AuthorAutocompleteFilter,
    )
    search_fields = ("author__username",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "author")
