from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from django.db.models import Sum
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404

from food.models import RecipeIngredient, ShoppingCart


class RelationHandler:
    add_serializer: ModelSerializer

    def _create_relation(self, model_class, obj_id, user):
        obj = get_object_or_404(self.queryset, pk=obj_id)
        try:
            model_class.objects.create(recipe=obj, user=user)
        except IntegrityError:
            return Response(
                {"error": "Рецепт уже был добавлен."},
                status=HTTP_400_BAD_REQUEST,
            )

        serializer = self.add_serializer(obj)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def _delete_relation(self, model_class, user, pk):
        try:
            obj = model_class.objects.get(recipe__id=pk, user=user)
            obj.delete()

        except model_class.DoesNotExist:
            return Response(
                {"error": f"{model_class.__name__} не существует"},
                status=HTTP_400_BAD_REQUEST,
            )

        return Response(status=HTTP_204_NO_CONTENT)


def create_shopping_cart(user):
    shopping_cart = []

    shopping_carts = ShoppingCart.objects.filter(user=user)
    if not shopping_carts.exists():
        return shopping_cart

    recipe_ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_recipe__user=user
    )

    ingredients = recipe_ingredients.values(
        "ingredient__name", "ingredient__measurement_unit"
    ).annotate(amount=Sum("amount"))

    shopping_cart = [
        f'{ing["ingredient__name"]}: \
        {ing["amount"]} - \
            {ing["ingredient__measurement_unit"]}.\n\n'
        for ing in ingredients
    ]

    return shopping_cart
