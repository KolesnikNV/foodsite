from django.core.validators import MinValueValidator
from django.db import transaction
from drf_base64.fields import Base64ImageField
from rest_framework import exceptions, serializers

from users.models import User
from users.serializers import CustomUserSerializer

from .custom_fields import Hex2NameColor
from .models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tags,
)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели RecipeIngredient."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeIngredientInputSerializer(serializers.ModelSerializer):
    """Сериализатор для входных данных модели RecipeIngredient."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ["id", "amount"]


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tags."""

    color = Hex2NameColor()

    class Meta:
        model = Tags
        fields = ["id", "name", "color", "slug"]


class RecipeTagsSerializer(serializers.ModelSerializer):
    """Сериализатор для связи модели Recipe с моделью Tags."""

    class Meta:
        model = Tags
        fields = ["id"]

    def to_internal_value(self, data):
        """Преобразует внешнее значение во внутреннее представление."""
        if isinstance(data, list):
            return [int(item) for item in data]
        return super().to_internal_value(data)


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User, представляющий автора рецепта."""

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
        """Получает значение, указывающее,
        подписан ли пользователь на автора."""
        return False


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рецептов."""

    author = CustomUserSerializer(read_only=True)
    tags = TagsSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        """Получает значение, указывающее, добавлен ли ингредиент
        в избранное у пользователя."""
        ingredients = RecipeIngredient.objects.select_related(
            "ingredient"
        ).filter(recipe=obj)
        serializer = RecipeIngredientSerializer(ingredients, many=True)
        return serializer.data

    def get_is_favorite(self, obj):
        """Получает значение, указывающее, добавлен ли рецепт
        в избранное у пользователя."""
        user = self.context["request"].user

        if user.is_anonymous:
            return False

        return FavoriteRecipe.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Получает значение, указывающее,
        находится ли рецепт в корзине покупок у пользователя."""
        user = self.context["request"].user

        if user.is_anonymous:
            return False

        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()

    class Meta:
        model = Recipe
        exclude = ("pub_date",)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    COOKING_TIME_VALIDATION_ERROR = (
        "Время приготовления должно быть 1 или более."
    )

    TAGS_VALIDATION_ERROR = "Нужно добавить хотя бы один тег."
    INGREDIENTS_VALIDATION_ERROR = "Нужно добавить хотя бы один ингредиент."
    DUPLICATE_INGREDIENTS_VALIDATION_ERROR = "Ингредиенты не могут повторяться"
    INGREDIENT_ID_ERROR = "Неверный идентификатор ингредиента."

    author = AuthorSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(), many=True
    )
    ingredients = RecipeIngredientInputSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(1, message=COOKING_TIME_VALIDATION_ERROR),
        )
    )

    def validate_tags(self, value):
        """Проверяет, что хотя бы один тег был выбран."""
        if not value:
            raise exceptions.ValidationError(self.TAGS_VALIDATION_ERROR)
        return value

    def validate_ingredients(self, value):
        """Проверяет, что хотя бы один ингредиент
        был выбран и нет повторяющихся ингредиентов."""
        if not value:
            raise exceptions.ValidationError(self.INGREDIENTS_VALIDATION_ERROR)

        ingredient_ids = [item["id"] for item in value]
        duplicate_ingredient_ids = {
            id for id in ingredient_ids if ingredient_ids.count(id) > 1
        }

        if duplicate_ingredient_ids:
            raise exceptions.ValidationError(
                self.DUPLICATE_INGREDIENTS_VALIDATION_ERROR
            )

        return value

    @transaction.atomic
    def get_ingredients_data(self, ingredients):
        """Получть ингредиенты из запроса."""
        ingredient_data = []
        for ingredient in ingredients:
            ingredient_id = ingredient["id"]
            amount = ingredient["amount"]
            try:
                ingredient_obj = Ingredient.objects.get(pk=ingredient_id)
            except Ingredient.DoesNotExist:
                raise exceptions.ValidationError(self.INGREDIENT_ID_ERROR)
            ingredient_data.append(
                {
                    "ingredient": ingredient_obj,
                    "amount": amount,
                }
            )
        return ingredient_data

    @transaction.atomic
    def create(self, validated_data):
        """Создает новый рецепт."""
        author = self.context.get("request").user
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)

        ingredient_data = self.get_ingredients_data(ingredients)
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(recipe=recipe, **data)
                for data in ingredient_data
            ]
        )

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет существующий рецепт."""
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.set(tags)

        ingredients = validated_data.pop("ingredients", None)
        if ingredients is not None:
            instance.ingredients.clear()

        ingredient_obj, amount = self.get_ingredients_data(ingredients)
        RecipeIngredient.objects.update_or_create(
            recipe=instance,
            ingredient=ingredient_obj,
            defaults={"amount": amount},
        )

        return super().update(instance, validated_data)

    @transaction.atomic
    def to_representation(self, instance):
        """Преобразует объект рецепта в его представление."""
        serializer = RecipeListSerializer(
            instance, context={"request": self.context.get("request")}
        )
        return serializer.data

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )
        extra_kwargs = {
            "ingredients": {"required": True, "allow_blank": False},
            "tags": {"required": True, "allow_blank": False},
            "name": {"required": True, "allow_blank": False},
            "text": {"required": True, "allow_blank": False},
            "image": {"required": True, "allow_blank": False},
            "cooking_time": {"required": True},
        }


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого представления рецепта."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ("recipe",)
