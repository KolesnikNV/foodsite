from django_filters import rest_framework as filters

from .models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """
    Класс фильтров для модели Ingredient.
    Поддерживает фильтрацию по имени (регистронезависимо).
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
        method="get_favorite",
        label="favorite",
    )
    tags = filters.AllValuesMultipleFilter(
        field_name="tags__slug",
        label="tags",
    )
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

    def get_favorite(self, queryset, name, value):
        """
        Фильтрует рецепты на основе того, добавлены ли они в избранное пользователем или нет.
        """
        if value:
            return queryset.filter(in_favorite__user=self.request.user)
        return queryset.exclude(in_favorite__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        """
        Фильтрует рецепты на основе того, находятся ли они в списке покупок пользователя или нет.
        """
        if value:
            return Recipe.objects.filter(
                shopping_recipe__user=self.request.user
            )
