from django.db.models import F, Model, Q, Sum
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)

from .models import Ingredient, ShoppingCart


class RelationHandler:
    add_serializer: ModelSerializer
    link_model: Model

    def _create_relation(self, obj_id):
        obj = get_object_or_404(self.queryset, pk=obj_id)
        try:
            self.link_model(None, obj.pk, self.request.user.pk).save()
        except IntegrityError:
            return Response(
                {"error": "Рецепт уже был добавлен."},
                status=HTTP_400_BAD_REQUEST,
            )

        serializer = self.add_serializer(obj)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def _delete_relation(self, q):
        deleted, _ = (
            self.link_model.objects.filter(q & Q(user=self.request.user))
            .first()
            .delete()
        )
        if not deleted:
            return Response(
                {"error": f"{self.link_model.__name__} не существует"},
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
