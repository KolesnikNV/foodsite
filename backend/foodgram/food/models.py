from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
from django.core.validators import MinValueValidator


class Ingredient(models.Model):
    name = models.CharField("Название", max_length=100, blank=False)
    unit = models.CharField("Единицы измерения", max_length=50, blank=False)

    def __str__(self):
        return self.name


class Tags(models.Model):
    name = models.CharField(
        "Название", max_length=100, blank=False, unique=True
    )
    color = models.CharField("Цвет", max_length=7, blank=False, unique=True)
    slug = models.SlugField("Слаг", unique=True, blank=False)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор рецепта",
        blank=False,
    )
    name = models.CharField("Название рецепта", max_length=100, blank=False)
    image = models.ImageField(
        "Изображение блюда", upload_to="images/", blank=False
    )
    text = models.TextField("Описание рецепта", max_length=500, blank=False)
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient", blank=False
    )
    tags = models.ManyToManyField(Tags, verbose_name="Тэги", blank=False)
    cooking_time = models.IntegerField(
        "Время приготовления в минутах",
        blank=False,
        validators=(
            MinValueValidator(
                1,
                message="Укажите время больше нуля!",
            ),
        ),
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField(
        "Количество",
        validators=(
            MinValueValidator(
                1,
                message="Укажите количество больше нуля!",
            ),
        ),
        blank=False,
    )
    unit = models.CharField("Единицы измерения", max_length=50, blank=False)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "recipe",
                    "ingredient",
                ),
                name="recipe_ingredient_unique",
            ),
        )
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"

    def __str__(self):
        return f"{self.ingredient.name} - {self.amount} {self.unit}"


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_("Рецепт"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь"),
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("recipe", "user"),
                name="unique_favorite",
            ),
        )
        ordering = ("-id",)
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные рецепты"

    def __str__(self):
        return f"Рецепт {self.recipe} в избранном пользователя {self.user}"


class ShoppingList(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_("Рецепт"),
        related_name="shopping_recipe",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь"),
        related_name="shopping_user",
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("recipe", "user"),
                name="shopping_recipe_user_exists",
            ),
        )
        ordering = ("-id",)
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

    def __str__(self):
        return f"Рецепт {self.recipe} у пользователя {self.user}"
