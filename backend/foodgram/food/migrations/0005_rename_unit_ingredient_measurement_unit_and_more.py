# Generated by Django 4.2.3 on 2023-07-12 11:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0004_alter_recipe_options_recipe_pub_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='unit',
            new_name='measurement_unit',
        ),
        migrations.RenameField(
            model_name='recipeingredient',
            old_name='unit',
            new_name='measurement_unit',
        ),
    ]
