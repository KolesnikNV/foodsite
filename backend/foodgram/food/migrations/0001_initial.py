# Generated by Django 4.2.3 on 2023-07-24 04:38

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FavoriteRecipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "Избранный рецепт",
                "verbose_name_plural": "Избранные рецепты",
                "ordering": ("-id",),
            },
        ),
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=100, verbose_name="Название"),
                ),
                (
                    "measurement_unit",
                    models.CharField(
                        max_length=50, verbose_name="Единицы измерения"
                    ),
                ),
            ],
            options={
                "verbose_name": "Ингредиент",
                "verbose_name_plural": "Ингредиенты",
            },
        ),
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100, verbose_name="Название рецепта"
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        upload_to="images/", verbose_name="Изображение блюда"
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        max_length=500, verbose_name="Описание рецепта"
                    ),
                ),
                (
                    "cooking_time",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                1, message="Укажите время больше нуля!"
                            )
                        ],
                        verbose_name="Время приготовления в минутах",
                    ),
                ),
                (
                    "pub_date",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Дата публикации рецепта",
                    ),
                ),
            ],
            options={
                "verbose_name": "Рецепт",
                "verbose_name_plural": "Рецепты",
                "ordering": ("-pub_date",),
            },
        ),
        migrations.CreateModel(
            name="RecipeIngredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                1, message="Укажите количество больше нуля!"
                            )
                        ],
                        verbose_name="Количество",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ингредиент в рецепте",
                "verbose_name_plural": "Ингредиенты в рецептах",
            },
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100, unique=True, verbose_name="Название"
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        max_length=7, unique=True, verbose_name="Цвет"
                    ),
                ),
                ("slug", models.SlugField(unique=True, verbose_name="Слаг")),
            ],
            options={
                "verbose_name": "Тэг",
                "verbose_name_plural": "Тэги",
            },
        ),
        migrations.CreateModel(
            name="ShoppingCart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shopping_recipe",
                        to="food.recipe",
                        verbose_name="Рецепт",
                    ),
                ),
            ],
            options={
                "verbose_name": "Список покупок",
                "verbose_name_plural": "Списки покупок",
                "ordering": ("-id",),
            },
        ),
    ]
