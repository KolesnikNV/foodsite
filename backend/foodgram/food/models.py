from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Ingredient(models.Model):
    """
    Модель для представления ингредиента.
    """

    name = models.CharField("Название", max_length=100, blank=False)
    measurement_unit = models.CharField(
        "Единицы измерения", max_length=50, blank=False
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self) -> str:
        return f"{self.name} - {self.measurement_unit}"


class Tag(models.Model):
    """
    Модель для представления тега.
    """

    name = models.CharField(
        "Название", max_length=100, blank=False, unique=True
    )
    color = models.CharField("Цвет", max_length=7, blank=False, unique=True)
    slug = models.SlugField("Слаг", unique=True, blank=False)

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    """
    Модель для представления рецепта.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор рецепта",
        related_name="recipes",
        blank=False,
    )
    name = models.CharField("Название рецепта", max_length=100, blank=False)
    image = models.ImageField(
        "Изображение блюда", upload_to="images/", blank=False
    )
    text = models.TextField("Описание рецепта", max_length=500, blank=False)
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        blank=False,
        related_name="recipes",
    )
    tags = models.ManyToManyField(
        Tag, verbose_name="Тэги", related_name="recipes", blank=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления в минутах",
        blank=False,
        validators=(
            MinValueValidator(
                1,
                message="Укажите время больше нуля!",
            ),
        ),
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации рецепта",
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Модель для представления ингредиента в рецепте.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredient",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество",
        validators=(
            MinValueValidator(
                1,
                message="Укажите количество больше нуля!",
            ),
        ),
        blank=False,
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="uq_recipe_ingredient",
            ),
        )
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"

    def __str__(self):
        return (
            f"{self.recipe.name}: "
            f"{self.ingredient.name} - "
            f"{self.amount} "
            f"{self.ingredient.measurement_unit}"
        )


class FavoriteRecipe(models.Model):
    """
    Модель для представления избранного рецепта.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="favorites",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="favorite_recipes",
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("recipe", "user"),
                name="uq_user_recipe",
            ),
        )
        ordering = ("-id",)
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"

    def __str__(self):
        return f"Рецепт {self.recipe} в избранном пользователя {self.user}"


class ShoppingCart(models.Model):
    """
    Модель для представления списка покупок.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="shopping_recipe",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
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
