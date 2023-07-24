from django.core.validators import MinValueValidator
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from food.custom_fields import Hex2NameColor
from food.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from rest_framework import exceptions, serializers
from users.models import Follow, User


class CurrentUserDefaultId(object):
    """
    Класс-фабрика для определения идентификатора текущего пользователя.
    """

    requires_context = True

    def __call__(self, serializer_instance=None):
        if serializer_instance is not None:
            self.user_id = serializer_instance.context["request"].user.id
            return self.user_id


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Пользовательский сериализатор для создания пользователя.
    """

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class CustomUserSerializer(UserSerializer):
    """
    Пользовательский сериализатор для модели User.
    """

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    email = serializers.EmailField(
        required=False, allow_null=True, allow_blank=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]

    def get_is_subscribed(self, obj):
        """
        Возвращает информацию о том,
        подписан ли текущий пользователь на
        переданного пользователя.
        """
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=self.context["request"].user, author=obj
        ).exists()


class FollowRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткой информации о рецепте в подписках.
    """

    class Meta:
        model = Recipe
        fields = ["id", "name", "image", "cooking_time"]


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для информации о подписке пользователя.
    """

    is_subscribed = serializers.SerializerMethodField(
        method_name="get_is_subscribed"
    )
    recipes = serializers.SerializerMethodField(method_name="get_recipes")
    recipes_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        ]

    def get_is_subscribed(self, obj):
        """
        Возвращает информацию о том,
        подписан ли текущий пользователь на
        переданного пользователя.
        """
        user = self.context.get("request").user
        if not user:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        """
        Возвращает информацию о рецептах пользователя,
        на которого подписан текущий пользователь.
        """
        request = self.context.get("request")
        recipes = obj.recipe_set.all()[:6]
        context = {"request": request}
        return FollowRecipeSerializer(recipes, many=True, context=context).data


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

    class Meta:
        model = RecipeIngredient
        fields = ["id", "amount"]


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tags."""

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ["id", "name", "color", "slug"]


class RecipeTagsSerializer(serializers.ModelSerializer):
    """Сериализатор для связи модели Recipe с моделью Tags."""

    class Meta:
        model = Tag
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
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        """Получает значение, указывающее, добавлен ли ингредиент
        в избранное у пользователя."""
        ingredients = RecipeIngredient.objects.select_related(
            "ingredient"
        ).filter(recipe=obj)
        serializer = RecipeIngredientSerializer(ingredients, many=True)
        return serializer.data

    def get_is_favorited(self, obj):
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

    name = serializers.CharField(required=True, allow_blank=False)
    text = serializers.CharField(required=True, allow_blank=False)
    author = AuthorSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = RecipeIngredientInputSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(1, message=COOKING_TIME_VALIDATION_ERROR),
        ),
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
        ingredient_ids = [ingredient["id"] for ingredient in ingredients]

        ingredients_queryset = Ingredient.objects.filter(pk__in=ingredient_ids)

        if not ingredients_queryset.exists():
            raise exceptions.ValidationError(self.INGREDIENT_ID_ERROR)

        ingredient_data = []

        for ingredient in ingredients:
            ingredient_id = ingredient["id"]
            amount = ingredient["amount"]

            ingredient_obj = ingredients_queryset.get(pk=ingredient_id)

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
