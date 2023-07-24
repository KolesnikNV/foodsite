from django_filters import rest_framework as filters

from .models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """
    Класс фильтров для модели Ingredient.
    Поддерживает фильтрацию по названию (регистронезависимо).
    """

    name = filters.CharFilter(
        field_name="name",
        lookup_expr="istartswith",
    )

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipeFilter(filters.FilterSet):
    """
    Фильтры для сортировки результатов рецептов:
    - по тегам
    - по наличию в избранном
    - по наличию в списке покупок.
    """

    is_favorited = filters.BooleanFilter(
        method="get_is_favorited",
    )
    tags = filters.BaseInFilter(field_name="tags__slug", lookup_expr="in")

    is_in_shopping_cart = filters.BooleanFilter(
        method="get_is_in_shopping_cart",
        label="shopping_cart",
    )

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_is_favorited(self, queryset, name, value):
        """
        Фильтрует рецепты на основе того,
        добавлены ли они в избранное пользователем или нет.
        """
        request = self.request
        user = request.user

        if user.is_authenticated:
            if value:
                return queryset.filter(favorites__user=user)
            return queryset.exclude(favorites__user=user)

        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """
        Фильтрует рецепты на основе того,
        находятся ли они в списке покупок пользователя или нет.
        """
        if value:
            return queryset.filter(shopping_recipe__user=self.request.user)
        return queryset.exclude(shopping_recipe__user=self.request.user)
