from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from food.models import Recipe

from .models import Follow

User = get_user_model()


# class CurrentUserDefaultId(object):
#     """
#     Класс-фабрика для определения идентификатора текущего пользователя.
#     """

#     requires_context = True

#     def __call__(self, serializer_instance=None):
#         if serializer_instance is not None:
#             self.user_id = serializer_instance.context["request"].user.id
#             return self.user_id


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

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        """
        Возвращает информацию о том, подписан ли текущий пользователь на переданного пользователя.
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
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для информации о подписке пользователя.
    """

    is_subscribed = serializers.SerializerMethodField(
        method_name="get_is_subscribed"
    )
    recipes = serializers.SerializerMethodField(method_name="get_recipes")
    recipes_count = serializers.SerializerMethodField(
        method_name="get_recipes_count"
    )

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
        Возвращает информацию о том, подписан ли текущий пользователь на переданного пользователя.
        """
        user = self.context.get("request").user
        if not user:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        """
        Возвращает информацию о рецептах пользователя, на которого подписан текущий пользователь.
        """
        request = self.context.get("request")
        recipes = obj.recipe_set.all()[:6]
        context = {"request": request}
        return FollowRecipeSerializer(recipes, many=True, context=context).data

    def get_recipes_count(self, obj):
        """
        Возвращает количество рецептов пользователя.
        """
        return Recipe.objects.filter(author=obj).count()
