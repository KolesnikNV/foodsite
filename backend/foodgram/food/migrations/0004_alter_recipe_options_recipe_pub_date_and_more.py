# Generated by Django 4.2.3 on 2023-07-11 15:21

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("food", "0003_alter_recipe_image_alter_recipeingredient_id"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="recipe",
            options={
                "ordering": ("-pub_date",),
                "verbose_name": "Рецепт",
                "verbose_name_plural": "Рецепты",
            },
        ),
        migrations.AddField(
            model_name="recipe",
            name="pub_date",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Дата публикации рецепта",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="recipeingredient",
            name="id",
            field=models.BigAutoField(
                auto_created=True,
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
        ),
    ]
