from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet

from .models import Tags, Recipe, Ingredient
from .serializers import (
    TagsSerializer,
    RecipeSerializer,
    RecipeListSerializer,
    IngredientSerializer,
)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.action == "create" or self.action == "update":
            return RecipeSerializer
        elif self.action == "list" or self.action == "retrieve":
            return RecipeListSerializer


class TagsViewSet(ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = PageNumberPagination


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = PageNumberPagination
