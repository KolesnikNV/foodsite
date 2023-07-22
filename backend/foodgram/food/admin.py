from django.contrib import admin
from django.db.models import Count

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    """
    Административный класс для модели Tags.
    """

    list_display = (
        "id",
        "name",
        "color",
        "slug",
    )
    search_fields = ("name",)
    ordering = ("color",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Административный класс для модели Ingredient.
    """

    list_display = (
        "id",
        "name",
        "measurement_unit",
        "get_recipes_count",
    )
    search_fields = ("name",)
    ordering = ("measurement_unit",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("recipeingredient_set")
        )

    def get_recipes_count(self, obj):
        """
        Возвращает количество рецептов, в которых используется ингредиент.
        """
        return RecipeIngredient.objects.filter(ingredient=obj.id).count()

    get_recipes_count.short_description = "Использований в рецептах"


class RecipeIngredientsInline(admin.TabularInline):
    """
    Встроенный административный класс для модели RecipeIngredient.
    """

    model = RecipeIngredient
    exclude = ("measurement_unit",)
    min_num = 1
    extra = 1


@admin.register(RecipeIngredient)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    """
    Административный класс для модели RecipeIngredient.
    """

    list_display = ("id", "recipe", "ingredient", "amount")
    list_filter = ("id", "recipe", "ingredient")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Административный класс для модели Recipe.
    """

    list_display = ("id", "name", "author", "in_favorite")
    list_filter = (
        "name",
        "author",
        "tags",
    )

    inlines = (RecipeIngredientsInline,)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("author")
            .prefetch_related("tags")
            .annotate(favorites_count=Count("in_favorite"))
        )

    def in_favorite(self, obj):
        """
        Возвращает количество раз, когда рецепт был добавлен в избранное.
        """
        return obj.favorites_count

    in_favorite.short_description = "Количество добавлений в избранное"


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    """
    Административный класс для модели FavoriteRecipe.
    """

    list_display = (
        "id",
        "user",
        "recipe",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "recipe")


@admin.register(ShoppingCart)
class ShoppingListAdmin(admin.ModelAdmin):
    """
    Административный класс для модели ShoppingCart.
    """

    list_display = (
        "id",
        "user",
        "recipe",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "recipe")
