from django.db.models import Q
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.mixin import MultiSerializerViewSetMixin
from api.relation_handler_for_views import RelationHandler, create_shoping_cart
from api.serializers import (
    FavoriteRecipe,
    IngredientSerializer,
    RecipeListSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    TagsSerializer,
)

from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Recipe, ShoppingCart, Tag
from .permissions import AdminOrReadOnly, AuthorOrStaffOrReadOnly


class RecipeViewSet(
    ModelViewSet, RelationHandler, MultiSerializerViewSetMixin
):
    """
    ViewSet для модели Recipe.
    Поддерживает операции CRUD:
    (create, retrieve, update, delete) и список рецептов.

    """

    queryset = Recipe.objects.select_related("author").prefetch_related(
        "tags", "ingredients"
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_class = (AuthorOrStaffOrReadOnly,)
    add_serializer = ShortRecipeSerializer
    pagination_class = PageNumberPagination
    serializer_classes = {
        "list": RecipeListSerializer,
        "retrieve": RecipeSerializer,
        "create": RecipeSerializer,
        "update": RecipeSerializer,
    }

    def get_serializer_class(self):
        """
        Возвращает класс сериализатора в зависимости от действия запроса.

        """
        return self.serializer_classes.get(self.action, RecipeSerializer)

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """
        Добавляет endpoint для добавления рецепта в избранное.

        """
        return

    @favorite.mapping.post
    def add_to_favorites(self, request, pk):
        """
        Добавляет рецепт в список избранных у текущего пользователя.

        """
        return self._create_relation(FavoriteRecipe, pk)

    @favorite.mapping.delete
    def delete_recipe_from_favorites(self, request, pk):
        """
        Удаляет рецепт из списка избранных у текущего пользователя.

        """
        return self._delete_relation(FavoriteRecipe, pk)

    @action(detail=True, permission_classes=[IsAuthenticated])
    def shopping_cart(self, pk):
        """
        Добавляет endpoint для добавления рецепта в список покупок.

        """
        return

    @shopping_cart.mapping.post
    def add_recipe_to_cart(self, request, pk):
        """
        Добавляет рецепт в корзину покупок текущего пользователя.

        """
        return self._create_relation(ShoppingCart, pk)

    @shopping_cart.mapping.delete
    def delete_recipe_from_cart(self, request, pk):
        """
        Удаляет рецепт из корзины покупок текущего пользователя.

        """
        return self._delete_relation(ShoppingCart, Q(recipe__id=pk))

    @action(
        methods=("get",), detail=False, permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """
        Выгружает список рецептов из корзины
        покупок текущего пользователя в текстовый файл.

        """
        user = request.user
        if not user.shopping_user.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        filename = f"{user.username}_shopping_cart.txt"
        shopping_cart = create_shoping_cart(user)
        response = HttpResponse(
            shopping_cart, content_type="text.txt; charset=utf-8"
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response


class TagsViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для модели Tags.
    Поддерживает только операции чтения списка тегов и деталей отдельного тега.

    """

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для модели Ingredient.
    Поддерживает только операции чтения
    списка ингредиентов и деталей отдельного ингредиента.

    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    filterset_class = IngredientFilter
    search_fields = ("^name",)
    pagination_class = None
