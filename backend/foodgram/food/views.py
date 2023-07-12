from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import filters
from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Recipe, Tags
from .serializers import (
    IngredientSerializer,
    RecipeListSerializer,
    RecipeSerializer,
    TagsSerializer,
)


class RecipeViewSet(ModelViewSet):
    """
    ViewSet для модели Recipe.
    Поддерживает операции CRUD (create, retrieve, update, delete) и список рецептов.

    """

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """
        Возвращает класс сериализатора в зависимости от действия запроса.

        """
        if self.action == "create" or self.action == "update":
            return RecipeSerializer
        elif self.action == "list" or self.action == "retrieve":
            return RecipeListSerializer
        return RecipeSerializer

    def get_queryset(self):
        """
        Возвращает queryset рецептов с использованием оптимизации запросов.

        """
        queryset = super().get_queryset()
        prefetch_tags = Prefetch("tags", queryset=Tags.objects.all())
        prefetch_ingredients = Prefetch(
            "recipeingredient_set__ingredient",
            queryset=Ingredient.objects.all(),
        )
        queryset = queryset.prefetch_related(
            prefetch_tags, prefetch_ingredients
        )
        return queryset


class TagsViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для модели Tags.
    Поддерживает только операции чтения списка тегов и деталей отдельного тега.

    """

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = PageNumberPagination


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для модели Ingredient.
    Поддерживает только операции чтения списка ингредиентов и деталей отдельного ингредиента.

    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)
