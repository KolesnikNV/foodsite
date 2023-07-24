from django.db.models import F, Sum
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from food.models import Ingredient, ShoppingCart
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)


class RelationHandler:
    add_serializer: ModelSerializer

    def _create_relation(self, model_class, obj_id):
        obj = get_object_or_404(self.queryset, pk=obj_id)
        try:
            model_class(None, obj.pk, self.request.user.pk).save()
        except IntegrityError:
            return Response(
                {"error": "Рецепт уже был добавлен."},
                status=HTTP_400_BAD_REQUEST,
            )

        serializer = self.add_serializer(obj)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def _delete_relation(self, model_class, q):
        try:
            obj = model_class.objects.get(q, user=self.request.user)
            obj.delete()
        except model_class.DoesNotExist:
            return Response(
                {"error": f"{model_class.__name__} не существует"},
                status=HTTP_400_BAD_REQUEST,
            )
        return Response(status=HTTP_204_NO_CONTENT)


def create_shoping_cart(user):
    shopping_cart = []

    shopping_carts = ShoppingCart.objects.filter(user=user)
    if not shopping_carts.exists():
        return shopping_cart

    ingredients = (
        Ingredient.objects.filter(
            recipeingredient__recipe__shopping_recipe__in=shopping_carts
        )
        .values("name", measurement=F("measurement_unit"))
        .annotate(amount=Sum("recipeingredient__amount"))
    )

    shopping_cart = [
        f'{ing["name"]}: {ing["amount"]} - {ing["measurement"]}.\n\n'
        for ing in ingredients
    ]

    return shopping_cart
