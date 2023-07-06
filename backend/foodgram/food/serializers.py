from rest_framework import serializers
from users.models import User
from .custom_fields import Hex2NameColor, Base64ImageField
from .models import (
    Tags,
    Recipe,
    Ingredient,
    RecipeIngredient,
    FavoriteRecipe,
    ShoppingList,
)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name", "unit"]


class Ingredients_in_recipe(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            "id": representation["id"],
            "amount": representation["amount"],
        }


class TagsSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tags
        fields = ["id", "name", "color", "slug"]


class Tags_in_recipe(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ["id"]

    def to_internal_value(self, data):
        if isinstance(data, list):
            return [int(item) for item in data]
        return super().to_internal_value(data)


class Author_in_recipe(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
        ]

    def get_is_subscribed(self, obj):
        return False


class RecipeListSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    author = Author_in_recipe()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "image",
            "text",
            "ingredients",
            "tags",
            "author",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        ]

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            recipe=obj, user=request.user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            recipe=obj, user=request.user
        ).exists()


class RecipeSerializer(serializers.ModelSerializer):
    tags = Tags_in_recipe()
    ingredients = Ingredients_in_recipe(many=True)
    author = serializers.SlugRelatedField(
        slug_field="username", read_only=True, required=False
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "image",
            "text",
            "ingredients",
            "tags",
            "author",
            "cooking_time",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        author = (
            request.user if request and request.user.is_authenticated else None
        )
        validated_data["author"] = author
        tags_data = validated_data.pop("tags", [])
        ingredients_data = validated_data.pop("ingredients", [])

        recipe = Recipe.objects.create(**validated_data)

        self.handle_ingredients(recipe, ingredients_data)
        self.handle_tags(recipe, tags_data)

        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop("tags", [])
        ingredients_data = validated_data.pop("ingredients", [])

        self.handle_ingredients(instance, ingredients_data)

        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.save()

        self.handle_tags(instance, tags_data)

        return instance

    def handle_ingredients(self, recipe, ingredients_data):
        recipe.ingredients.clear()
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data["id"])
            amount = ingredient_data["amount"]
            unit = ingredient.unit
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount, unit=unit
            )

    def handle_tags(self, recipe, tags_data):
        recipe.tags.clear()
        for tag_id in tags_data:
            tag = Tags.objects.get(id=tag_id)
            recipe.tags.add(tag)

    def get_author(self, obj):
        return obj.author.id
